import requests
import frappe
from frappe import _
import xml.etree.ElementTree as ET

@frappe.whitelist()  
def get_form_data():
    cust_name = frappe.get_list("Letter of Credit", fields=["*"])
    return cust_name

def get_session_id():
    url="http://192.168.240.14:8080/WFRestFulWebServices/ngone/Restful/slcabone/WMConnect/?userName=supervisor&UserExist=N"
    headers={
        "Content-Type": "application/xml",
        "password":"System@123"
    }
    xml_body="""
            <?xml version="1.0"?>
        <WMConnect_Output>
            <Option>WMConnect</Option>
            <Exception>
                <MainCode>0</MainCode>
            </Exception>
            <Participant>
                <ID>1</ID>
                <LastLoginTime>2024-10-01 15:31:16.427</LastLoginTime>
                <IsAdmin>Y</IsAdmin>
                <Privileges>1111111111111111111111111</Privileges>
            </Participant>
            <LastLoginTime>2024-10-01 15:31:16.427</LastLoginTime>
            <LastLoginFailureTime></LastLoginFailureTime>
            <FailureAttemptCount>0</FailureAttemptCount>
            <TimeZoneInfo>
                <DBServer>
                    <OffSet>345</OffSet>
                </DBServer>
            </TimeZoneInfo>
        </WMConnect_Output>
"""
    try:
        response = requests.post(url, data=xml_body, headers=headers)
        root = ET.fromstring(response.content)
        session_id = root.findtext('.//SessionId')
        if session_id:
            frappe.msgprint(f"Session ID: {session_id}")
            return session_id
    except:
        frappe.throw("Session ID not found in the response. User might already be logged in.")



def send_data_to_platform(doc,session_id):
    url="http://192.168.240.14:8080/WFRestFulWebServices/ngone/Restful/slcabone/WFUploadWorkItem"
    params={
        "processDefId": "2",
        "initiateFromActivityId": "2",
        "attributes":(
            f"LCcifID{doc.cif_id}"
            f"LCapplicantName{doc.applicant_name}"
            f"LCaccountNumber{doc.account_number}"
            f"LCapplicantAddress{doc.applicant_address}"
            f"LCapplicantPhone{doc.phone}"
            f"LCemail{doc.applicant_email}"
            f"LCpostalCode{doc.postal_code}"
            f"LCpanNo{doc.pan_no}"
            f"LCbeneficiaryName{doc.custom_beneficiary_name}"
            f"LCcountry{doc.custom_country}"
            f"LCbProvince{doc.custom_province}"
            f"LCcity{doc.custom_city}"
            f"LCstreet{doc.custom_street}"
            f"LCpostalCodeBeneficiary{doc.custom_postal}"
            f"LCbEmail{doc.custom_email}"
            f"LCMobileCode{doc.custom_mobile_code}"
            f"LCbPhone{doc.custom_phone_no}"
            
        )
    }
    headers={
        "sessionid":session_id
    }
    try:
        response = requests.post(url, params=params, headers=headers)
        
        # Logging request and response details for debugging
        frappe.logger().info(f"Request URL: {url}")
        frappe.logger().info(f"Request Headers: {headers}")
        frappe.logger().info(f"Request Params: {params}")
        frappe.logger().info(f"Response Status Code: {response.status_code}")
        frappe.logger().info(f"Response Content: {response.content}")

        if response.status_code == 200:
            # Parse XML response
            root = ET.fromstring(response.text)
            description_element = root.find('.//ProcessInstanceId')
            print(description_element)
            if description_element is not None:
                process_id = description_element.text
                print(process_id)
                frappe.msgprint(f"Data has been successfully pushed with PID {process_id}.")
            else:
                frappe.msgprint("ProcessInstanceId tag not found in the XML response.")
        else:
            frappe.throw(_("Failed to push data to the third-party application. Status Code: {0}").format(response.status_code))

    except requests.exceptions.RequestException as e:
        frappe.logger().error(f"Request error occurred: {e}")
        frappe.throw(_("Request error occurred: {0}").format(e))
    except ET.ParseError as e:
        frappe.logger().error(f"Error parsing XML: {e}")
        frappe.throw(_("Error parsing XML: {0}").format(e))
    except Exception as err:
        frappe.logger().error(f"An error occurred while pushing data: {err}")
        frappe.throw(_("An error occurred while pushing data: {0}").format(err))


def disconnect_session(session_id):
    url = "http://192.168.240.14:8080/WFRestFulWebServices/ngone/Restful/slcabone/WMDisconnect?userName=supervisor"
    headers = {
        "Content-Type": "application/xml",
        "SessionID": session_id
    }
    
    # Prepare the XML body for disconnecting the session
    xml_body = f"""
    <WMDisConnect_Input>
        <Option>WMDisConnect</Option>
        <EngineName>ofcab</EngineName>
        <SessionID>{session_id}</SessionID>
        <UnlockWorkitem>Y</UnlockWorkitem>
    </WMDisConnect_Input>
    """
    
    # Send the disconnect request
    response = requests.post(url, headers=headers)
    
    if response.status_code != 200:
        frappe.throw(_("Failed to disconnect session"))
    else:
        frappe.msgprint("Session Released")

def main(doc,method):
    session_id = get_session_id()
    
    try:
        cust_data = get_form_data()
        #print("got customer data")

        send_data_to_platform(doc,session_id)
        #print("success")
        #frappe.msgprint(_("All customer data sent successfully."))
    
    finally:
        disconnect_session(session_id)



if __name__=="__main__":
    main()
