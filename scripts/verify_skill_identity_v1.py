"""Mesh Skill identity validation. Read-only; no repository scripts are executed."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import PurePosixPath

SEMVER = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?\Z')
EXCLUDED = {'tests', 'fixtures', 'generated', 'dist', 'node_modules', '.venv', '__pycache__'}


def version_key(value):
    if not isinstance(value, str):
        raise ValueError('version must be a string')
    m = SEMVER.fullmatch(value)
    if not m:
        raise ValueError('invalid SemVer: ' + repr(value))
    pre = m.group(4)
    items = []
    for part in pre.split('.') if pre is not None else []:
        if part.isdigit():
            if len(part) > 1 and part[0] == '0':
                raise ValueError('leading zero in prerelease: ' + value)
            items.append((0, int(part)))
        else:
            items.append((1, part))
    return tuple(map(int, m.group(1, 2, 3))), pre is None, tuple(items)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field: ' + key)
        result[key] = value
    return result


def identity(text, name, version, repository, root):
    value = json.loads(text, object_pairs_hook=unique_object)
    expected = dict(schema='mesh.skill-metadata.v1', name=name, version=version,
                    source_repository=repository, source_path=root)
    if not isinstance(value, dict):
        raise ValueError('metadata must be an object')
    for field, wanted in expected.items():
        if value.get(field) != wanted:
            raise ValueError('metadata ' + field + ' does not match source identity')
    return value


def progression(old_version, new_version, changed, managed):
    """Only the first addition of identity files can keep the prior version."""
    new_key = version_key(new_version)
    old_key = version_key(old_version) if old_version is not None else None
    if old_key is not None and new_key < old_key:
        raise ValueError('version regression')
    bootstrap = not managed and set(changed) <= {'VERSION', 'metadata/skill.json'}
    if changed and not bootstrap and old_key is not None and new_key <= old_key:
        raise ValueError('changed Skill package requires a SemVer increase')
    if changed and not bootstrap and old_key is None:
        raise ValueError('cannot establish version progression for changed legacy Skill')
    return 'BOOTSTRAP' if bootstrap and changed else 'VERSIONED'


def git(*args):
    p = subprocess.run(['git', '--no-pager', '-c', 'core.hooksPath=/dev/null', *args],
                       capture_output=True, timeout=45, check=False)
    if p.returncode:
        raise ValueError('git ' + args[0] + ' failed')
    return p.stdout


def tree(ref):
    rows = {}
    for record in git('ls-tree', '-rz', '--full-tree', ref).split(b'\0'):
        if not record:
            continue
        header, rawpath = record.split(b'\t', 1)
        mode, kind, oid = header.decode('ascii').split()
        path = rawpath.decode('utf-8')
        parts = PurePosixPath(path).parts
        if path.startswith('/') or '..' in parts or any(ord(c) < 32 for c in path):
            raise ValueError('unsafe repository path')
        rows[path] = (mode, kind, oid)
    return rows


def read_text(rows, path):
    row = rows.get(path)
    if row is None or row[0] not in {'100644', '100755'} or row[1] != 'blob':
        raise ValueError('missing or nonregular file: ' + path)
    data = git('cat-file', 'blob', row[2])
    if len(data) > 1024 * 1024:
        raise ValueError('oversize metadata or entrypoint: ' + path)
    return data.decode('utf-8')


def validate(repository, base=None):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('repository identity required')
    head = git('rev-parse', 'HEAD').decode().strip()
    now = tree(head)
    prior = {}
    if base and set(base) != {'0'}:
        if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', base):
            raise ValueError('base must be an exact commit SHA')
        prior = tree(base)
    entrypoints = [p for p in now if PurePosixPath(p).name.lower() == 'skill.md'
                   and not EXCLUDED.intersection(PurePosixPath(p).parts)]
    if not entrypoints:
        raise ValueError('no governed Skills found; inventory must not silently disappear')
    found = set()
    rows, errors = [], []
    for entry in sorted(entrypoints):
        root = str(PurePosixPath(entry).parent)
        prefix = '' if root == '.' else root + '/'
        try:
            text = read_text(now, entry).replace('\r\n', '\n')
            front = re.match(r'^---\n(.*?)\n---(?:\n|$)', text, re.S)
            if not front:
                raise ValueError('missing YAML frontmatter')
            names = re.findall(r'^name:\s*([^\n]+)', front.group(1), re.M)
            if len(names) != 1:
                raise ValueError('exactly one frontmatter name is required')
            name = names[0].strip().strip('\"\'')
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
                raise ValueError('invalid Skill identifier')
            if name in found:
                raise ValueError('duplicate Skill identifier')
            found.add(name)
            version = read_text(now, prefix + 'VERSION').strip()
            version_key(version)
            identity(read_text(now, prefix + 'metadata/skill.json'), name, version, repository, root)
            described = re.search(r'(?m)^description:.*?Skill version ([^ ]+)\. ', front.group(1))
            if described and described.group(1) != version:
                raise ValueError('description version differs from VERSION')
            files = {p: x for p, x in now.items() if p.startswith(prefix)
                     and not EXCLUDED.intersection(PurePosixPath(p[len(prefix):]).parts)
                     and not p[len(prefix):].startswith('.github/')}
            if any(x[0] not in {'100644', '100755'} for x in files.values()):
                raise ValueError('nonregular file in governed package')
            changed = {p[len(prefix):] for p in set(now) | set(prior)
                       if p.startswith(prefix) and now.get(p) != prior.get(p)
                       and not EXCLUDED.intersection(PurePosixPath(p[len(prefix):]).parts)
                       and not p[len(prefix):].startswith('.github/')}
            state = 'BASELINE_ONLY'
            if prior and entry in prior:
                old = read_text(prior, prefix + 'VERSION').strip() if prefix + 'VERSION' in prior else None
                # Legacy family VERSION is used only as a declared bootstrap comparison basis.
                if old is None and 'VERSION' in prior and not changed <= {'VERSION', 'metadata/skill.json'}:
                    old = read_text(prior, 'VERSION').strip()
                state = progression(old, version, changed, prefix + 'metadata/skill.json' in prior)
            filemap = [[p[len(prefix):], *files[p]] for p in sorted(files)]
            digest = hashlib.sha256(json.dumps(filemap, separators=(',', ':')).encode()).hexdigest()
            rows.append(dict(name=name, version=version, source_repository=repository, source_path=root,
                             source_commit=head, source_git_manifest_sha256=digest,
                             file_count=len(files), progression=state))
        except (ValueError, UnicodeError, json.JSONDecodeError) as e:
            errors.append(root + ': ' + str(e))
    result = dict(schema='mesh.skill-version-verification.v1', repository=repository,
                  source_commit=head, base_commit=base, skill_count=len(rows),
                  status='FAIL' if errors else 'PASS', skills=rows, errors=errors)
    return result


def self_test():
    ordered = ['1.0.0-alpha','1.0.0-alpha.1','1.0.0-alpha.beta','1.0.0-beta',
               '1.0.0-beta.2','1.0.0-beta.11','1.0.0-rc.1','1.0.0','1.0.1','2.0.0']
    assert sorted(reversed(ordered), key=version_key) == ordered
    assert version_key('1.0.0+x') == version_key('1.0.0+y')
    for bad in ['1.2', '01.2.3', '1.2.3-01', '1.2.3-', '1.2.3-a..b', '1.2.3+', 123]:
        try:
            version_key(bad)
        except ValueError:
            continue
        raise AssertionError('accepted invalid version ' + repr(bad))
    progression('1.0.0','1.0.0',{'metadata/skill.json'},False)
    progression('1.0.0-rc.1','1.0.0',{'SKILL.md'},True)
    for old, new, changed, managed in [
        ('1.0.0','1.0.0',{'SKILL.md'},True),
        ('1.0.0','1.0.0',{'metadata/skill.json'},True),
        ('1.0.0','1.0.0+new',{'SKILL.md'},True),
        ('1.0.0','0.9.9',set(),False),
        ('1.0.0','1.0.0-rc.1',{'SKILL.md'},True),
        (None,'1.0.0',{'SKILL.md'},False),
    ]:
        try:
            progression(old,new,changed,managed)
        except ValueError:
            continue
        raise AssertionError('accepted invalid progression')
    good = dict(schema='mesh.skill-metadata.v1',name='test-skill',version='1.0.0',
                source_repository='example/repo',source_path='skills/test-skill')
    identity(json.dumps(good),'test-skill','1.0.0','example/repo','skills/test-skill')
    for key in good:
        bad = dict(good); bad.pop(key)
        try:
            identity(json.dumps(bad),'test-skill','1.0.0','example/repo','skills/test-skill')
        except ValueError:
            continue
        raise AssertionError('accepted missing identity ' + key)
    try:
        json.loads('{"version":"1.0.0","version":"2.0.0"}',object_pairs_hook=unique_object)
    except ValueError:
        pass
    else:
        raise AssertionError('accepted duplicate metadata key')
    print('PASS: SemVer, prerelease, build metadata, identity and progression self-tests')


if __name__ == '__main__':
    self_test()
    if '--self-test' not in sys.argv:
        result = validate(os.environ.get('GITHUB_REPOSITORY',''), os.environ.get('BASE_SHA'))
        output = os.path.join(os.environ.get('RUNNER_TEMP', '/tmp'), 'skill-version-verification.json')
        with open(output,'x',encoding='utf-8') as f:
            json.dump(result,f,indent=2); f.write('\n')
        print(json.dumps(result,indent=2))
        raise SystemExit(bool(result['errors']))
