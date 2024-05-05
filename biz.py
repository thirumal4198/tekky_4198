import streamlit as st
import pandas as pd
import sqlite3
import easyocr
from PIL import Image
import numpy as np
import base64
import io

def extract_data(img_path): # input as object
    img = Image.open(img_path)
    img_arr = np.array(img) # Replace 'path_to_image.jpg' with the actual path to the uploaded image
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img_arr,detail=0)
    return results, img

def extract_information(ocr_results):
    cardholder_name = ocr_results[0]
    company_name = ''
    designation = ''
    mobile_numbers = []
    email_address = ''
    website_url = ''
    address = ''
    Pincode = ''

    for text in ocr_results:

        if any(char.isalpha() for char in text):
            company_name = text

        if any(word in text.lower() for word in ['manager', 'executive', 'ceo', 'founder', 'president']):
            designation = text

        if any(char.isdigit() for char in text) and '-' in text:
            mobile_numbers.append(text)

        if '@' in text and '.' in text:
            email_address = text

        if 'www' in text.lower() or '.com' in text.lower() and '@' not in text:
            website_url = text

        if any(char.isdigit() for char in text) and any(char.isalpha() for char in text) and '@' not in text:
            address += text + ' '

        if (text.isdigit() and len(text) == 6):
            Pincode = text

    address = address.strip()

    import re
    pincode_regex = r"\b\d{6,7}\b"
    pincodes = re.findall(pincode_regex, address)
    if pincodes:
        Pincode = pincodes[0]

    address = re.sub(pincode_regex, '', address)

    extracted_info = {
        'CardHolderName': cardholder_name,
        'CompanyName': company_name,
        'Designation': designation,
        'MobileNumbers': ', '.join(mobile_numbers),
        'EmailAddress': email_address,
        'WebsiteURL': website_url,
        'Address': address,
        'Pincode': Pincode
    }

    return extracted_info

def fetch_data():
    mydb = sqlite3.connect('b.db')
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM bizcard_details")
    rows = cursor.fetchall()
    return rows

#streamlit Part
st.set_page_config(layout='wide')
st.title('Bizcardx: Business Card Data Extraction')
col1,col2,col3 = st.columns([1,1,1])
with col1:
  uploaded_file = st.file_uploader('Upload Business Card Image',type=['jpg','png','jpeg'])
with col2:
  if uploaded_file is not None:
      st.image(uploaded_file,width =500)
if uploaded_file is not None:
    #st.image(uploaded_file,width =300)
    text_img, input_img = extract_data(uploaded_file)
    extracted_info = extract_information(text_img)
    col1,col2 = st.columns(2)
    with col1:
      for key,values in extracted_info.items():
          extracted_info[key]= st.text_input(key,values)
    with col2:
      df = pd.DataFrame([extracted_info])
      data = df.transpose()
      data.columns = ['DETAILS']
      st.dataframe(data)

    Confirm = st.button('Confirm & Upload')
    if Confirm:
        st.write('uploaded')
        mydb = sqlite3.connect('b.db')
        cursor = mydb.cursor()

        #table creation
        create_table_query = '''CREATE TABLE IF NOT EXISTS bizcard_details (
                              cardholdername varchar(255),
                              companyname varchar(255),
                              designation varchar(255),
                              mobilenumbers varchar(255),
                              emailaddress varchar(255),
                              websiteurl text ,
                              address text,
                              pincode varchar(255),
                              uploaded_image BLOB
                          )'''
        #st.write("CREATE TABLE query:", create_table_query)  # Debug statement

        cursor.execute(create_table_query)
        mydb.commit()

        # Fetch the column names from the created table
        # Insert query
        mydb = sqlite3.connect('b.db')
        cursor = mydb.cursor()
        insert_query = '''INSERT INTO bizcard_details (cardholdername, companyname, designation, mobilenumbers, emailaddress,
                                                      websiteurl, address, pincode, uploaded_image)
                                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        # Convert the image to bytes and store in the database
        img_bytes = uploaded_file.getvalue()
        data = df.values.tolist()[0]
        data.append(img_bytes)
        cursor.execute(insert_query, data)
        mydb.commit()
        #print(1)
        st.success('successfully uploaded')


    st.title('Database Table')
    #search_term = st.text_input("Search for:")
    #if search_term:
        #filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        #st.write(filtered_df)

    if st.button('Refresh'):
        # Fetch data from the database again
        rows = fetch_data()
        if rows:
            df = pd.DataFrame(rows, columns=['CardHolderName','CompanyName', 'Designation', 'MobileNumbers',
                                             'EmailAddress', 'WebsiteURL', 'Address', 'Pincode', 'UploadedImage'])
            # Display the updated DataFrame
            st.write(df)
    else:
        rows = fetch_data()
        if rows:
            df = pd.DataFrame(rows, columns=['CardHolderName', 'CompanyName', 'Designation', 'MobileNumbers',
                                             'EmailAddress', 'WebsiteURL', 'Address', 'Pincode', 'UploadedImage'])
            # Display the updated DataFrame
            st.write(df)


    # Fetch data from the database
    rows = fetch_data()
    if rows:
        df = pd.DataFrame(rows, columns=['CardHolderName', 'CompanyName', 'Designation', 'MobileNumbers',
                                         'EmailAddress', 'WebsiteURL', 'Address', 'Pincode', 'UploadedImage'])

        # Display uploaded images
        for index, row in df.iterrows():
            if row['UploadedImage'] is not None:
                image = Image.open(io.BytesIO(row['UploadedImage']))
                #st.image(image, caption=f"Uploaded Image - {row['CardHolderName']}", use_column_width=False)

        # Add select box for each row
        cardholder_names = df['CardHolderName'].tolist()
        selected_cardholder_names = st.multiselect('Select cardholder names', cardholder_names)

        # Add remove button

        # Add modify button
        if st.button('View/Modify'):
            for card_holder_name in selected_cardholder_names:
                # Get the values of the selected row
                company_name = df.loc[df['CardHolderName'] == card_holder_name, 'CompanyName'].iloc[0]
                designation = df.loc[df['CardHolderName'] == card_holder_name, 'Designation'].iloc[0]
                mobile_numbers = df.loc[df['CardHolderName'] == card_holder_name, 'MobileNumbers'].iloc[0]
                email_address = df.loc[df['CardHolderName'] == card_holder_name, 'EmailAddress'].iloc[0]
                website_url = df.loc[df['CardHolderName'] == card_holder_name, 'WebsiteURL'].iloc[0]
                address = df.loc[df['CardHolderName'] == card_holder_name, 'Address'].iloc[0]
                pincode = df.loc[df['CardHolderName'] == card_holder_name, 'Pincode'].iloc[0]
                uploaded_image = df.loc[df['CardHolderName'] == card_holder_name, 'UploadedImage'].iloc[0]

                # Display input fields to modify the values
                col1,col2 = st.columns(2)
                with col1:
                  new_company_name = st.text_input('Company Name', company_name, key=f'company_name_{card_holder_name}')
                  new_designation = st.text_input('Designation', designation, key=f'designation_{card_holder_name}')
                  new_mobile_numbers = st.text_input('Mobile Numbers', mobile_numbers, key=f'mobile_numbers_{card_holder_name}')
                  new_email_address = st.text_input('Email Address', email_address, key=f'email_address_{card_holder_name}')
                  new_website_url = st.text_input('Website URL', website_url, key=f'website_url_{card_holder_name}')
                  new_address = st.text_input('Address', address, key=f'address_{card_holder_name}')
                  new_pincode = st.text_input('Pincode', pincode, key=f'pincode_{card_holder_name}')
                with col2:
                  if uploaded_image is not None:
                    image = Image.open(io.BytesIO(uploaded_image))
                    st.image(image, caption=f"Uploaded Image - {card_holder_name}", width=500)
                # Update the selected row in the database
                mydb = sqlite3.connect('b.db')
                cursor = mydb.cursor()

                cursor.execute("UPDATE bizcard_details SET CompanyName=?, Designation=?, "
                                "MobileNumbers=?, EmailAddress=?, WebsiteURL=?, Address=?, Pincode=? "
                                "WHERE CardHolderName=?", (new_company_name, new_designation,
                                                            new_mobile_numbers, new_email_address, new_website_url,
                                                            new_address, new_pincode, card_holder_name))
                mydb.commit()
                st.success('All changes saved')
                break  # Exit the loop after updating the first selected row

        if st.button('Remove'):

            # Remove selected rows from the database table
            mydb = sqlite3.connect('b.db')
            cursor = mydb.cursor()
            for card_holder_name in selected_cardholder_names:
                cursor.execute("DELETE FROM bizcard_details WHERE CardHolderName=?", (card_holder_name,))
            mydb.commit()
            st.write('Data removed')

if __name__ == '__main__':
    pass
