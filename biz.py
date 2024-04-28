import streamlit as st
import pandas as pd
import sqlite3
import easyocr
from PIL import Image
import numpy as np
import base64

def extract_data(img_path):
    img = Image.open(img_path)
    img_arr = np.array(img)
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img_arr,detail=0)
    return results, img

def extract_information(ocr_results):
    company_name = ''
    cardholder_name = ocr_results[0]
    designation = ''
    mobile_numbers = []
    email_address = ''
    website_url = ''
    address = ''
    Pincode = ''

    for text in ocr_results:
        if 'digitals' in text.lower():
            company_name = 'Selva Digitals'
        elif any(char.isalpha() for char in text):
            company_name = text

        if any(word in text.lower() for word in ['manager', 'executive', 'ceo', 'founder', 'president']):
            designation = text

        if any(char.isdigit() for char in text) and '-' in text:
            mobile_numbers.append(text)

        if '@' in text and '.' in text:
            email_address = text

        if 'www' in text.lower() and '.' in text.lower() and '@' not in text:
            website_url = text

        if any(char.isdigit() for char in text) and any(char.isalpha() for char in text) and '@' not in text:
            address += text + ' '

        if text.isdigit() and len(text) == 6:
            Pincode = text

    address = address.strip()

    extracted_info = {
        'Company Name': company_name,
        'Card Holder Name': cardholder_name,
        'Designation': designation,
        'Mobile Numbers': ', '.join(mobile_numbers),
        'Email Address': email_address,
        'Website URL': website_url,
        'Address': address,
        'Pincode': Pincode
    }

    return extracted_info


# Create a Streamlit app
st.title('BizCardX: Business Card Data Extraction')

# File uploader for business card image
uploaded_file = st.file_uploader("Upload Business Card Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, width=300)
    text_img, input_img = extract_data(uploaded_file)
    extracted_info = extract_information(text_img)
    for key, value in extracted_info.items():
        if key != 'Mobile Numbers':  # Display mobile numbers in a text area
            extracted_info[key] = st.text_input(key, value)
        else:
            extracted_info[key] = st.text_area(key, value)
    if st.button("Confirm Information"):
        # Convert extracted information to DataFrame
        df = pd.DataFrame([extracted_info])

        # Convert image to base64 encoded string
        img_str = base64.b64encode(uploaded_file.read()).decode('utf-8')

        # Add a new column to the DataFrame containing the base64 encoded image
        df['Uploaded Image'] = [img_str]

        st.dataframe(df)  # Display DataFrame using st.dataframe()
        if st.button('Upload'):
            # Establish connection to SQLite database
            conn = sqlite3.connect('/root/biz.db')
            c = conn.cursor()
            # Create table if not exists
            c.execute('''CREATE TABLE IF NOT EXISTS biz_table (
                         CompanyName TEXT,
                         CardHolderName TEXT,
                         Designation TEXT,
                         MobileNumbers TEXT,
                         EmailAddress TEXT,
                         WebsiteURL TEXT,
                         Address TEXT,
                         Pincode TEXT,
                         UploadedImage TEXT
                         )''')
            # Insert data into the table
            c.execute('''INSERT INTO biz_table (CompanyName, CardHolderName, Designation, MobileNumbers, EmailAddress, WebsiteURL, Address, Pincode, UploadedImage)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (extracted_info['Company Name'],
                         extracted_info['Card Holder Name'],
                         extracted_info['Designation'],
                         extracted_info['Mobile Numbers'],
                         extracted_info['Email Address'],
                         extracted_info['Website URL'],
                         extracted_info['Address'],
                         extracted_info['Pincode'],
                         img_str))

            # Commit changes and close connection
            conn.commit()
            conn.close()
            st.write('Data uploaded successfully.')

    method = st.radio('Select the method',['None','preview','Modify'])
    
    if method=='None':
      st.write('')
    

    if method == 'Preview':
      mydb = sqlite3.connect('biz.db')
      cursor = mydb.cursor()

      select_query = 'Select * from biz_table'
      cursor.execute(select_query)
      table= cursor.fetchall()
      mydb.commit()

      table_df - pd.DataFrame(table, columns=('CompanyName', 'CardHolderName', 'Designation', 'MobileNumbers',
                                             'EmailAddress', 'WebsiteURL','Address','Pincode','UploadedImage') )
      st.dataframe(table_df)

    elif method=='Modify':
      mydb = sqlite3.connect('biz.db')
      cursor = mydb.cursor()

      select_query = 'Select * from biz_table'
      cursor.execute(select_query)
      table= cursor.fetchall()
      mydb.commit()

      table_df - pd.DataFrame(table, columns=('CompanyName', 'CardHolderName', 'Designation', 'MobileNumbers',
                                             'EmailAddress', 'WebsiteURL','Address','Pincode','UploadedImage') )
      
      col1,col2 = st.column(2)
      with col1:
        selected_name = st.selectbox('Select the Name', table_df['CardHolderName'])
      df_3 = table_df[table_df['CardHolderName']== selected_name]

      
      df_4 = df_3.copy()
      

      col1,col2 = st.columns(2)
      with col1:
        mo_name = st.text_input('Name',df-3['CardHolderName'].unique()[0])
        mo_desi = st.text_input('Designation',df-3['CardHolderName'].unique()[0])
        mo_com_name = st.text_input('CompanyName',df-3['CompanyName'].unique()[0])
        mo_contact = st.text_input('MobileNumbers',df-3['MobileNumbers'].unique()[0])
        mo_email = st.text_input('EmailAddress',df-3['EmailAddress'].unique()[0])

        df_4['Name']= mo_name
        df_4['Designation']= mo_desi
        df_4['CompanyName']= mo_com_name
        df_4['MobileNumbers']= mo_contact
        df_4['EmailAddress']= mo_email

      with col2:
        mo_website = st.text_input('WebsiteURL',df-3['WebsiteURL'].unique()[0])
        mo_address = st.text_input('Address',df-3['Address'].unique()[0])
        mo_pincode = st.text_input('Pincode',df-3['Pincode'].unique()[0])
        mo_image = st.text_input('UploadedImage',df-3['UploadedImage'].unique()[0])

        df_4['WebsiteURL']= mo_website
        df_4['Address']= mo_address
        df_4['Pincode']= mo_pincode
        df_4['UploadedImage']= mo_image
      
      st.dataframe(df_4)
      col1,col2 = st.columns(2)
      with col1:
        button_3 = st.button('Modify', use_container_width = True)

      if button_3:
        mydb = sqlite3.connect('biz.db')
        cursor = mydb.cursor()

        cursor.execute(f'Delete from table wherer name = "{selected_name}"')
        mydb.commit()

        st.success('Saved Successfully')


elif select == 'Delete':
  
  mydb = sqlite3.connect('biz.db')
  cursor = mydb.cursor()

  col1,col2 = st.columns(2)
  
  with col1:
    select_query = 'select CardHolderName from biz_table'

    cursor.execute(select_query)
    table1 = cursor.fetchall()
    mydb.commit()

    name=[]

    for i in table1:
      names.append(i[0])

    name_select = st.selectbox('select the name',names)
  
  with col2:
    select_query = 'select Designation from biz_table where CardHolderName = '{name_select}''

    cursor.execute(select_query)
    table2 = cursor.fetchall()
    mydb.commit()

    Designations=[]

    for j in table1:
      Designations.append(j[0])

    Designation_select = st.selectbox('select the designation',Designations)

  if name_select and designation_select:
    col1,col2,col3 = st.columns(3)

    with col1:
      st.write(f"selected Name : {name_select}")
      st.write('')
      st.write('')
      st.write('')
      st.write(f'Selected Designation : {designation_select}')
     
    with col2:
      st.write('')
      st.write('')
      st.write('')
      st.write('')

      remove = st.buton('Delete', use_container width = True)

      if remove:
        cursor.execute(f"Delete from biz_table where CardHolderName = '{name_select}' and Designation = '{designation_select}'" )
        mydb.commit(
            
        st.warning('Deleted')
        )
# Run Streamlit app
if __name__ == "__main__":
    pass
