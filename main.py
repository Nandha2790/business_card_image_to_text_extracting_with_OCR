import streamlit as st
import easyocr
import re
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import streamlit as st
from PIL import Image
import io
import numpy as np
import cv2
import matplotlib.pyplot as plt
import mysql.connector


st.title("BizCardX - Extracting business card Data with OCR ")

with st.sidebar:
    st.markdown("# Upload image")

image = st.sidebar.file_uploader("**Browse the image**",type=["png", "jpg", "jpeg"])

tab1,tab2,tab3 = st.tabs(["The OCR Output","Verify Data", "Modify & Delete Biz Card"])

engine = create_engine('mysql+pymysql://root:pwd123@127.0.0.1/biz_card')

with tab1:
    col1, col2 = st.columns([5,5])
    
    if image is None:
        
        col1.subheader("Upload the business card image to convert data")


    reader = easyocr.Reader(['en'])


    email_re = r"[a-zA-z0-9._+-]+@[a-zA-Z0-9]+.[a-zA-Z]{3,4}"
    mobile_no_re = r"[+0-9-]{9,13}"
    website_re = r"[WWWwww].+[A-Za-z0-9].+[A-Za-z]{3,4}"
    street_re = r"[\d]{3,5}\s+[a-zA-Z]+\s[a-zA-Z]+\s,+\s+[a-zA-Z]+"
    street_re_1 = r"[\d]{3,5}\s+[a-zA-Z]+\s[a-zA-Z]+.+"
    state_re = r"[a-zA-z]+[A-Za-z]\s+[\d]{6,7}"
    state_re_1 = r"[\d]{6,7}"

    if image:
        image_data = image.read()
        image_stream = io.BytesIO(image_data)
        image_pil = Image.open(image_stream)
        image_np = np.array(image_pil)
        col1.subheader("The uploaded image")
        
        col1.image(image_np, caption='Uploaded Image', use_column_width=True)   

        results = reader.readtext(image_np,height_ths=0.7,slope_ths=0.5 )
        
        col1.subheader("Boundry boxes over the text")
        
        for t in results:
            bbox, text, score = t
            cv2.rectangle(image_np,bbox[0], bbox[2],(0,255,0),5)
            
            
        col1.image(image_np,channels="BGR")
        
        group_1 = [results[0],results[1]]
        results.remove(group_1[0])
        results.remove(group_1[1])
        results.sort(key=lambda x: x[0][0][1])
        height = [(results[i][0][2][1] - results[i][0][0][1]) for i in range(len(results))]
        height.sort()
        group_2 = []
        group_3 =[]
        if (height[-1] - height[-2])<=20:
            for i in range(len(results)):
                height_bbox = results[i][0][2][1] - results[i][0][0][1]
                if height_bbox<height[-2]:
                    group_2.append(results[i][1])
                else:
                    group_3.append(results[i][1])
        else:
            for i in range(len(results)):
                height_bbox = results[i][0][2][1] - results[i][0][0][1]
                if height_bbox<height[-1]:
                    group_2.append(results[i][1])
                else:
                    group_3.append(results[i][1])
                    
        
        def text_processing (text):
            catgories = ['email_id','mobile_no','website','street_and_city','state_and_pincode']
            biz_table = {i:[] for i in catgories}

            for i in text:
                email_match = re.search(email_re,i)
                if email_match:
                    biz_table["email_id"].append(email_match.group())
                    continue

                mobile_match = re.search(mobile_no_re,i)
                if mobile_match:
                    biz_table["mobile_no"].append(mobile_match.group())
                    continue

                website_match = re.search(website_re,i)
                if website_match:
                    biz_table["website"].append(website_match.group())
                    continue

                street_match = re.search(street_re,i)
                street_match_1 = re.search(street_re_1,i)
                if street_match or street_match_1:
                    if street_match_1:
                        biz_table["street_and_city"].append(street_match_1.group())
                    elif street_match:
                        biz_table["street_and_city"].append(street_match.group())                
                    continue

                state_match = re.search(state_re,i)
                state_match_1 = re.search(state_re_1,i)
                if state_match or state_match_1:
                    if state_match:
                        biz_table["state_and_pincode"].append(state_match.group())
                    elif state_match_1:
                        biz_table["state_and_pincode"].append(state_match_1.group())
                        
            return biz_table
        
        com_name = []
        if len(group_3)>1:
            com_name.append(group_3[0]+" "+group_3[1])
        else:
            com_name.append(group_3[0])


        def biz_card_details():
            
            t = text_processing(group_2)
            street_city = re.split(r'[,;]',t['street_and_city'][0])
            if '' in street_city:
                street_city.remove('')
            state_pincode =[ i.split(" ") for i in t['state_and_pincode'] ]

            if len(t['mobile_no'])>1:
                email_id = t['email_id'][0]
                mobile_number_1 = t['mobile_no'][0]
                mobile_number_2 = t['mobile_no'][1]
                website = t['website'][0]
                street = street_city[0]
                city = street_city[1]
                if len(street_city)>2:
                    state =street_city[2]
                else:   
                    state =state_pincode[0][0]
                if len(state_pincode[0])==1:
                    pincode = state_pincode[0][0]
                else:
                    pincode = state_pincode[0][1]

            else:
                email_id = t['email_id'][0]
                mobile_number_1 = t['mobile_no'][0]
                mobile_number_2 = "-"
                website = t['website'][0]
                street = street_city[0]
                city = street_city[1]
                if len(street_city)>2:
                    state =street_city[2]
                else:  
                    state =state_pincode[0][0]
                if len(state_pincode[0])==1:
                    pincode = state_pincode[0][0]
                else:
                    pincode = state_pincode[0][1]  
                    
            df = pd.DataFrame([{"Name": group_1[0][1],"Designation": group_1[1][1],"Email_id":email_id, "Mobile_number-1": mobile_number_1, "Mobile_number-2": mobile_number_2,"Company_Name": com_name[0] , "Website": website, "Street": street, "City": city, "State":state, "Pincode": pincode}])
            return df

        biz_card= biz_card_details()
        table_name = biz_card['Name'][0].lower()
        if " " in table_name:
            table_name1 = table_name.replace(" ","_")
        else:
            table_name1 = table_name
            
        com_name1 = biz_card['Company_Name'][0].lower()
        if " " in com_name1:
            com_name2 = com_name1.replace(" ","_")
        else:   
            com_name2 = com_name1
        col2.subheader("Extracted data from the uploaded image") 
        biz_card_df1 = biz_card.transpose()
        biz_card_df2 = biz_card_df1.rename(columns={0:"Details"}).reset_index()
        biz_card_df3 = biz_card_df2.rename(columns={"index":"Description"})
        col2.table(biz_card_df3)        

        df_edited = tab2.data_editor(biz_card,use_container_width=True)
        Mysql_export = tab2.button("Save to MySQL")
        
        if Mysql_export:
            df_edited.to_sql(f"{com_name2 + "_" + table_name1 }",con = engine,if_exists="replace",index=False)
            
            connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "pwd123", database = "biz_card")
            cursor = connection.cursor()
            alter_query = f"ALTER TABLE {com_name2 + '_' + table_name1} ADD COLUMN image LONGBLOB"
            cursor.execute(alter_query)
            connection.commit()
            cursor.close()
            connection.close()
            
            connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "pwd123", database = "biz_card")
            cursor = connection.cursor()
            image_insert_query = f"UPDATE {com_name2 + '_' + table_name1} SET image = %s"
            cursor.execute(image_insert_query, (image_data,))
            connection.commit()
            cursor.close()
            connection.close()             
            
            tab2.success(f"Successfully saved table name as {com_name2 + '_' + table_name1} in biz_card Database")

show_tables_query = "show tables;"

tab3.table(pd.read_sql_query(show_tables_query,con=engine))  
    
sql_tables_to_modify = tab3.selectbox("Biz_cards to modify",pd.read_sql_query(show_tables_query,con=engine))

tab3.markdown(f"#### Table Name : {sql_tables_to_modify}")    

modify_query = f"select * from {sql_tables_to_modify};"

df_modify = pd.read_sql_query(modify_query,con=engine)

df_update_table = tab3.dataframe(df_modify)

df_col = tab3.selectbox("selete columns to modify",df_modify.columns)

modify_data = tab3.text_input("Modify the data",placeholder="enter your value")

update_table = tab3.button("Update table")

if update_table:
           
    connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "pwd123", database = "biz_card")
    cursor = connection.cursor()
    modify_col_query  = f" UPDATE {sql_tables_to_modify} SET {df_col} = '{modify_data}';"
    cursor.execute(modify_col_query)
    connection.commit()
    cursor.close()
    connection.close()   

    tab3.success(f"{sql_tables_to_modify} table has been updated")


try:       
    
    sql_tables = tab3.selectbox("Biz_cards to delete",pd.read_sql_query(show_tables_query,con=engine))

    table_to_delete = tab3.button("Delete table")

    if table_to_delete:
        drop_query = f"drop table {sql_tables};"
        pd.read_sql_query(drop_query,con=engine)
        tab3.success(f"{sql_tables} table has been deleted")

except Exception as e:
    pass 
    
        
            