import streamlit as st
import openai
import os
import time
from streamlit_ace import st_ace
from primehub import PrimeHub, PrimeHubConfig


def gen_code():
    # Sidebar contents
    openai_api_key = st.sidebar.text_input('OpenAI API Key', '', type="password")
    openai.api_key = openai_api_key

    prompt = st.text_area('Please give the requirements that can gen code.', '', height=200)
    prompt_complete = """請輸出Python 程式碼，讓使用者可以只要運行'Python script.py'，即可直接運作。使用者的要求為：{}""".format(prompt)
    if st.button('Submit the prompt'):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a machine learning engineer"},
                {"role": "user", "content": prompt_complete},
            ]
        )
        data = completion['choices'][0]['message']['content']
        st.markdown(data)

def modify_code_and_save():
    # Spawn a new Ace editor
    st.text("Code: ")
    content = st_ace("", language="python")

    # 將文字寫入檔案
    if st.button('Submit the code'):
        timestamp = time.time()
        formatted_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(timestamp))
        file_name = os.path.join(os.getcwd(), "result", "gen_code_{}.py".format(formatted_time))

        with open(file_name, "w") as file:
            file.write(content)
            st.text("File path: {}".format(file_name))

def run_code():
    def get_latest_updated_file(folder_path):
        # Ensure the folder path exists
        if not os.path.exists(folder_path):
            raise ValueError("Folder path does not exist.")

        # Get a list of files in the folder along with their last modification times
        files_with_mtime = [(os.path.join(folder_path, file), os.path.getmtime(os.path.join(folder_path, file))) for file in os.listdir(folder_path)]

        # Find the file with the latest modification time
        latest_file_path, _ = max(files_with_mtime, key=lambda item: item[1])

        return latest_file_path
    
    latest_file_path = get_latest_updated_file(os.path.join(os.getcwd(), "result"))
    file_path = st.sidebar.text_input('File path:', latest_file_path)
    primehub_endpoint = st.sidebar.text_input('PrimeHub endpoint:', '')
    primehub_token = st.sidebar.text_input('PrimeHub token:', '', type="password")
    primehub_group = st.sidebar.text_input('PrimeHub group:', '')
    
    primehub_token_file_name = os.path.join(os.getcwd(), ".primehub", "config.json")
    if not os.path.exists(os.path.join(os.getcwd(), ".primehub")):
        os.mkdir(os.path.join(os.getcwd(), ".primehub"))
    
    if st.sidebar.button('Run the Code'):
        ph = PrimeHub(PrimeHubConfig())
        ph.config.set_endpoint("{}/api/graphql".format(primehub_endpoint))
        ph.config.set_token(primehub_token)
        ph.config.set_group(primehub_group)

        st.text(ph.is_ready())
        
        config = {
            "instanceType": "cpu-1",
            "image": "tf-2.5",
            "displayName": "gen-code-and-run",
            "command": "python3 {}".format(file_path),
        }

        run_job = ph.jobs.submit(config)
        st.text(run_job)
        st.text("Please check the information here:")
        st.text("{}/console/g/{}/job/{}".format(primehub_endpoint, primehub_group, run_job['id']))
    

def main():
    # 創建一個下拉框選擇分頁
    page_list = ["Step 1: Generate the Code", "Step 2: Modify and save the code", "Step 3: Run the code"]
    page = st.sidebar.selectbox("Subpage: ", page_list)
    
    st.title('Gen Code and Run.')

    # 根據選擇的分頁顯示內容
    if page == "Step 1: Generate the Code":
        gen_code()
    elif page == "Step 2: Modify and save the code":
        modify_code_and_save()
    elif page == "Step 3: Run the code":
        run_code()

if __name__ == "__main__":
    main()