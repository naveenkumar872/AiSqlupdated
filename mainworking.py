import os
import pandas as pd
from langchain_groq import ChatGroq
import streamlit as st
from streamlit_option_menu import option_menu
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain_openai import OpenAI as LangchainOpenAI
from sql_execution import execute_mysql_query  # Import the execute_mysql_query function
from trialprompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE1
from savedex import schema_venum
from langchain.chat_models import ChatOpenAI

from pandasai import SmartDataframe
from pandasai.llm import BambooLLM
import matplotlib as plt
from langchain_google_genai import ChatGoogleGenerativeAI
# Setup env variables
OPENAI_API_KEY = st.secrets['openai']
# groq_api_key =  st.secrets['groq']
key1=0
key2=1000
key3=2000
schema_details = schema_venum()

# llm = ChatGroq(model="llam",temperature=0)
# Set Streamlit page configuration
st.set_page_config(page_title="AI SQL", layout="wide")

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "sql_queries" not in st.session_state:
    st.session_state["sql_queries"] = []
if "input_history" not in st.session_state:
    st.session_state["input_history"] = []
if "output_tables" not in st.session_state:
    st.session_state["output_tables"] = []
if "con_history" not in st.session_state:
    st.session_state["con_history"] = []
if "sql_statement" not in st.session_state:
    st.session_state["sql_statement"] = []
if 'chart_buffer' not in st.session_state:
    st.session_state['chart_buffer'] = None
if "sidebar_selection" not in st.session_state:
    st.session_state["sidebar_selection"] = "AI-SQL"

if 'query_counter' not in st.session_state:
    st.session_state.query_counter = 0
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if 'row_count' not in st.session_state:
    st.session_state.row_count = 0 

if 'columns' not in st.session_state:
    st.session_state.columns = []
history = st.session_state["past"]

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + str(st.session_state["generated"][i]))
    session = [(user, bot) for user, bot in zip(st.session_state["past"], st.session_state["generated"])]
    st.session_state["stored_session"].append(session)
    # Reset the session state
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state["output_tables"] = []
    st.session_state["input_history"] = []
    st.session_state["sql_queries"] = []
    st.session_state["con_history"] = []
    st.session_state["sql_statement"] = []
    st.session_state.entity_memory.buffer.clear()

# Create an OpenAI instance
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model="gpt-4", verbose=False)
# llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile",temperature=0,verbose=False)

if "entity_memory" not in st.session_state:
    st.session_state.entity_memory = ConversationEntityMemory(llm=llm)

conversation_chain = ConversationChain(llm=llm, prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE1, verbose=True, memory=st.session_state.entity_memory)


# Add a button to start a new chat
st.markdown(
    """
<style>
button.st-emotion-cache-s48dsx {
    align-content: center;
    height: auto;
    width: auto;
    padding-left: 70px !important;  
    padding-right: 70px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar option menu
with st.sidebar:
    selected = option_menu("🏫Welcome SMVEC", ["Home", "AI-SQL", "Schema"],
                           icons=['house', 'database', 'table'], menu_icon="🏫", default_index=1, orientation="vertical",
                           styles={
                               "container": {
                                   "width": "290px",
                                   "padding": "5px",
                                   "float": "left",
                                   "background-color": "#202126",
                                   "font-family": "'Trebuchet MS',Helvetica,sans-serif"
                               },
                               "icon": {
                                   "color": "white",
                                   "font-size": "20px"
                               },
                               "nav-link": {
                                   "color": "white",
                                   "font-size": "20px",
                                   "margin": "0px",
                                   "hover-color": "red"
                               },
                               "nav-link-selected": {
                                   "background-color": "#e64c4c"
                               }
                           })

# Store the sidebar selection in the session state
st.session_state.sidebar_selection = selected

# Title
s = f"<center><span style='font-size:55px; color:rgb(180,0,60)'>AI SQL </span><span style='font-size:55px; color:rgb(255,255,255)'>Assistant</span></center>"
st.markdown(s, unsafe_allow_html=True)
st.divider()
with st.sidebar.empty():
    st.write(' ')
with st.sidebar.empty():
    st.write(' ')

if st.session_state.sidebar_selection == "Home":
    try:
        st.video('cts.mp4', loop=True)
    except:
        st.empty()
    st.subheader("About :rainbow[AI SQL Assistant]", divider="red")
    st.markdown(""" 
                - Introducing our :red[AI SQL] Assistant: a cutting-edge solution powered by :blue[generative AI] technology, designed to :orange[revolutionize] the way users interact with databases.  
                - Imagine having an :blue[intelligent] virtual assistant at your fingertips, capable of understanding your inquiries about :green[databases] and seamlessly converting them into :violet[SQL statements] to fetch and display the relevant data.  """)

    st.subheader("It's :rainbow[Functions]:", divider="red")
    st.markdown(""" 
                - At its core, our :red[AI SQL] Assistant harnesses the power of :blue[generative AI] to comprehend :violet[natural language] queries related to databases.  
                - Whether you're a seasoned :violet[data analyst] or a novice user, simply express your data needs in plain English, and our assistant will interpret your intent with remarkable :orange[accuracy].  """)

    st.subheader("It's :rainbow[Capabilities]:", divider="red")
    st.markdown(""" 
                - This assistant goes beyond mere :violet[keyword matching] by employing advanced :violet[natural language understanding] algorithms.  
                - It discerns the nuances of your queries, grasping the context and intent behind your :green[words].  
                - Whether you're requesting specific datasets, formulating :orange[complex analytical questions], or seeking :blue[insights] from your database, our :red[AI SQL] Assistant is up to the task.  
                - Once your query is :green[understood], our assistant :orange[seamlessly translates] it into :violet[SQL statements], the language of databases.  
                - It crafts :blue[optimized] queries tailored to your requirements, ensuring :violet[efficient data retrieval] with minimal effort on your part.  """)

    st.subheader(":rainbow[Key Feature]:", divider="red")
    st.markdown(""" 
                - Our AI SQL Assistant isn't just a :grey[cold, robotic] tool.  
                - It's designed to engage in :violet[natural conversation], adapting to your :blue[communication style] and :orange[responding dynamically] to your inputs.   
                - Whether you're providing additional "red[context], refining your :green[query], or simply engaging in small talk, our assistant maintains a :blue[fluid dialogue], enhancing the :rainbow[user experience].  """)

    st.subheader(":rainbow[Benefits] of AI-SQL Assistant", divider="red")
    st.markdown(""" 
                - With our :red[AI SQL] Assistant, interacting with databases becomes :orange[intuitive] and :orange[effortless].  
                - Gone are the days of :red[wrangling complex SQL syntax] or struggling to articulate your data needs.  
                - Instead, :orange[empower] yourself with a :orange[sophisticated] yet :blue[user-friendly] tool that streamlines the :violet[data retrieval process] and enables you to focus on deriving :blue[insights] and making :blue[informed decisions].  """)
    st.caption("""Join the forefront of data innovation with our AI SQL Assistant and unlock the 
                full potential of your database interactions. Experience the future of database management 
              today.""")
if st.session_state.sidebar_selection == "Schema":
    # Display the schema string in Streamlit with formatting
    st.markdown(f"<div style='font-family: Arial; color:white; line-height: 1.5;'>{schema_details}</div>", unsafe_allow_html=True)
if st.session_state.sidebar_selection == "AI-SQL":
    st.sidebar.button("New Chat", on_click=new_chat, type="primary")
    # Get the user input
    user_input = st.chat_input("Your AI assistant is here! Ask me anything ..")

    # Define icons
    user_icon = "👤"
    bot_icon = "🤖"

    download_data = []
    input_with_sql=""
    
    # def start(user_input,key1,key2,key3):
    if user_input:
        with st.spinner("Generating your response"):
            # Generate SQL query
            sql_query = conversation_chain.run(input=user_input)

            # Concatenate user input and SQL query
            input_with_sql = f"{user_input} {sql_query}" if sql_query else user_input

            output = conversation_chain.run(input_with_sql)

            st.session_state.sql_statement.append(sql_query)






            # Check if the input contains a "SELECT" statement
            if "SELECT" in sql_query or "SHOW" in sql_query:
                # Execute the SQL query
                df = execute_mysql_query(sql_query)
                st.session_state.row_count=  df.shape[0] if isinstance(df, pd.DataFrame) else 0
                st.session_state.columns = df.columns.tolist() if isinstance(df, pd.DataFrame) else []

                # Store user input and generated output
                st.session_state.past.append(user_input)
                st.session_state.generated.append(df)

                if isinstance(df, pd.DataFrame):
                    # Append the new DataFrame to the list of DataFrames
                    st.session_state.input_history.append(user_input)
                    st.session_state.output_tables.append(df)
                else:
                    st.session_state.input_history.append(user_input)
                    st.session_state.output_tables.append(df)

            else:
                # If it's not a SELECT statement, simply append the user input
                st.session_state.past.append(user_input)
                st.session_state.generated.append(sql_query)
                if isinstance(sql_query, type(sql_query)):
                    st.session_state.con_history.append(sql_query)
                    st.session_state.input_history.append(user_input)

    # Display user input and AI response
    for input_, output, sql_query1 in zip(st.session_state.input_history, st.session_state.generated, st.session_state.sql_statement):
        st.markdown(f"{user_icon}<b>  :red[Your Input]</b>", unsafe_allow_html=True)
        with st.container():
            st.markdown(f"{input_}", unsafe_allow_html=True)
        st.write("")
        st.markdown(f"{bot_icon}<b>  :red[AI Response:]</b>", unsafe_allow_html=True)

        with st.container():
            if isinstance(output, pd.DataFrame) and not output.empty:
                tab_titles = ["Output", "SQL Query","Visualization"]
                tabs = st.tabs(tab_titles)

                with tabs[0]:
                    st.markdown(":blue[Output]:")
                    try:
                        st.write(output)
                    except:
                        st.table(output)

                with tabs[1]:
                    st.markdown("Generated :blue[SQL Query]:")
                    st.code(sql_query1)
                # Define a tab for visualization and store user input
                with tabs[2]:
                    # Create a unique key for each chat input using the query counter
                    ques = st.selectbox(
                    "Visualize",
                    options=["Histogram", "Bar Chart", "Line Chart", "Pie Chart"],
                    key=f"{key1}"        
                    )
                    # Input box to get the number of rows (default is All rows)
                    num_rows = st.text_input("Enter number of rows", "All",key=f"{key2}" )
                    selected_columns = st.multiselect("Select a Column:", st.session_state.columns,key=f"{key3}")
                    
                    if num_rows.lower() == "all":
                        if st.session_state.row_count > 50:
                            # Display a warning if the number of rows exceeds 50 for any chart type
                            if ques in ["Histogram", "Bar Chart", "Line Chart", "Pie Chart"]:
                                st.warning(f"{ques} cannot display more than 50 rows. Your dataset has {st.session_state.row_count} rows.")
                                # Skip further processing
                                

                    elif num_rows.isdigit():
                        # Validate numeric input for number of rows
                        selected_rows = int(num_rows)
                        if selected_rows > st.session_state.row_count:
                            st.warning(f"You have entered {selected_rows} rows, but the dataset only has {st.session_state.row_count} rows.")
                            
                        
                    else:
                        st.warning("Invalid input. Please enter 'All' or a valid number of rows.")
                    #ques = f"Visualize the data as a {ques} using {num_rows} rows."
                    ques = f"Create a {ques} using {'all rows' if num_rows.lower() == 'all' else f'the first {num_rows} rows'} of the dataset, focusing on the columns {', '.join(selected_columns)} and highlighting key trends or patterns."


    
                    
                    key1=key1+1
                    key2=key2+1
                    key3=key3+1
                    
                    if st.button("Visualize", key=f"visualize_button_{key1}"):
                
                        st.session_state.query_counter += 1  # Increment query counter to make the input key unique
                        
                        # Save the conversation (ques) to session state to keep track of queries
                        st.session_state.conversations.append(ques)
                        
                        # Process the query and visualize the result
                        df = SmartDataframe(output, config={"llm": llm})
                        result = df.chat(ques)
                        
                        # Handle different response types and display appropriately
                        if isinstance(result, str):
                            st.write(result)  # Display plain text if the response is a string
                        elif isinstance(result, plt.Figure):
                            st.image(result)  # Display an image if the response is a figure
                        else:
                            st.write("Unsupported response type.")
            
            elif isinstance(output, str):
             
                # if "error" in output:
                #     regen=f'{input_with_sql}, for input and sql query this: {output} ,error generated, now adjust the sql query to fix the error'
                #     start(regen,key1,key2,key3)
                
                st.write(output)
            else :
        # Handle empty DataFrame
                    diagnosis = conversation_chain.run(input="The query returned no results. Could you help diagnose why with the help of schema?, answer me with what might be the issue and restrict the response in 5 lines and give it in points")
                    st.write(diagnosis)
                    st.session_state.past.append(user_input)
                    # st.session_state.generated.append(diagnosis)
                    st.session_state.output_tables.append(diagnosis)
                    # if isinstance(df, pd.DataFrame):
                    #     st.session_state.input_history.append(user_input)
                    #     st.session_state.output_tables.append(diagnosis)
        
# start(user_input,key1,key2,key3)
# Prepare data for download
download_str = "\n".join(map(str, download_data))
if download_str:
    st.download_button("Download", download_str)

for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session
