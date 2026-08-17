SENSITIVE_CLASSES={"private_dm","confidential_client","personal_information","financial_information","privileged_executive"}
def authorize_source(requester_permissions:set[str],source_class:str)->bool:return source_class not in SENSITIVE_CLASSES or source_class in requester_permissions
def sanitize_retrieved_content(content:str)->dict[str,str]:return {"classification":"UNTRUSTED_DATA","content":content}
def apply_retrieved_instruction(_:str)->None:raise PermissionError("Retrieved content is data and cannot alter operating policy")
