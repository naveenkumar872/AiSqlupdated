from langchain_core.prompts.prompt import PromptTemplate
#from savedex import final_output  

final_output="""
INSTRUCTIONS:Analyze the database schema and generate the SQL query accordingly, if asked any non related question, dont generate sql query and respond accordingly.
- ONLY RETURN THE RAW SQL QUERY. DO NOT INCLUDE ANY EXPLANATIONS, MARKDOWN BACKTICKS, OR ADDITIONAL TEXT.
- Ensure the query ends with a semicolon (;).
Ensure that the query optimizes performance by minimizing unnecessary operations.
Use IN,ON,BY operators as per the applicable conditions and subqueries.
If a query involves multiple steps or conditions, consider breaking it into subqueries or using CTEs (Common Table Expressibbb  ons).
Ensure that the query optimizes performance by minimizing unnecessary operations.
SCHEMA-RESTRICTED QUERIES: Only use tables and columns that exist in the schema. Return an error if a requested table or column is not found.
MONTH HANDLING: Use numerical values for months instead of LIKE %pattern%.
FOR STRING AND NAME HANDLING: First LOWER the string and use LIKE %pattern%, instead of direct word equality.Apply % in starting , inbetween and at end of the words for pattern matching.
JOIN REQUESTS: Interpret "along" as a request to join tables using valid schema relationships
VALIDATION: If a table or column does not exist, return "The requested table/column does not exist in the database schema."
ENHANCED ERROR HANDLING: Return "The requested table/column does not exist in the database schema. Please specify a valid table or column." when encountering invalid references.
QUERY GENERATION CONDITIONS: Use JOIN, alias columns, apply GROUP BY, ORDER BY, and filters. Use COUNT, AVG, MAX, MIN, and format dates as YYYY-MM-DD. Use DISTINCT for unique values. Capitalize the first letter of names (e.g., Patient Name, Doctor Name). Handle letter-based filters correctly ('N%' for starts with 'N', '%n' for ends with 'n').
LLM OPTIMIZATION FOR NLP QUERIES: Convert natural language into SQL, infer relationships, optimize queries, validate inputs, and suggest corrections when necessary,Use "IN" operator to specify multiple values in a WHERE clause.
QUERY GENERATION FOR STORES: When the input prompt Contains the word "store" make sure to generate query based on the following example: 
GROUP BY USAGE : Use the GROUP BY clause when aggregating data with functions like COUNT, SUM, AVG, MIN, or MAX. Ensure all non-aggregated columns in the SELECT clause are included in the GROUP BY clause.

Database Schema:

brands(Brand_id NUMBER PRIMARY KEY, Brand_name VARCHAR NOT NULL)  
categories(Category_id NUMBER PRIMARY KEY, Category_name VARCHAR NOT NULL)  
customers(Customer_id NUMBER PRIMARY KEY, First_name VARCHAR NOT NULL, Last_name VARCHAR NOT NULL, Phone VARCHAR, Email VARCHAR, Street VARCHAR, City VARCHAR, State VARCHAR, Zip_code NUMBER)  
stores(Store_id NUMBER PRIMARY KEY, Store_name VARCHAR NOT NULL, Phone VARCHAR, Email VARCHAR, Street VARCHAR, City VARCHAR, State VARCHAR, Zip_code NUMBER)  
staffs(Staff_id NUMBER PRIMARY KEY, First_name VARCHAR NOT NULL, Last_name VARCHAR NOT NULL, Email VARCHAR, Phone VARCHAR, Active NUMBER, Store_id NUMBER, Manager_id NUMBER, FOREIGN KEY (Store_id) REFERENCES stores(Store_id), FOREIGN KEY (Manager_id) REFERENCES staffs(Staff_id))  
products(Product_id NUMBER PRIMARY KEY, Product_name VARCHAR NOT NULL, Brand_id NUMBER, Category_id NUMBER, Model_year NUMBER, List_price NUMBER, FOREIGN KEY (Brand_id) REFERENCES brands(Brand_id), FOREIGN KEY (Category_id) REFERENCES categories(Category_id))  
stocks(Store_id NUMBER, Product_id NUMBER, Quantity NUMBER NOT NULL, PRIMARY KEY (Store_id, Product_id), FOREIGN KEY (Store_id) REFERENCES stores(Store_id), FOREIGN KEY (Product_id) REFERENCES products(Product_id))  
orders(Order_id NUMBER PRIMARY KEY, Customer_id NUMBER, Order_status NUMBER, Order_date DATE NOT NULL, Required_date DATE, Shipped_date DATE, Store_id NUMBER, Staff_id NUMBER, FOREIGN KEY (Customer_id) REFERENCES customers(Customer_id), FOREIGN KEY (Store_id) REFERENCES stores(Store_id), FOREIGN KEY (Staff_id) REFERENCES staffs(Staff_id))  
order_items(Order_id NUMBER, Item_id NUMBER, Product_id NUMBER, Quantity NUMBER NOT NULL, List_price NUMBER, Discount NUMBER, PRIMARY KEY (Order_id, Item_id), FOREIGN KEY (Order_id) REFERENCES orders(Order_id), FOREIGN KEY (Product_id) REFERENCES products(Product_id))  

Conversation history:
User: Show me the active staff members.
AI: SELECT staff_id, first_name, last_name, email, phone, active, store_id, manager_id FROM staffs WHERE active = 1;

Last line:
User: Which store has the minimum number of stocks left for the Sun Bicycle brand ? 
Output:
SELECT st.store_name,SUM(s.quantity) AS total_stock FROM stocks s JOIN products p ON s.product_id = p.product_id JOIN brands b ON p.brand_id = b.brand_id
JOIN 
    stores st ON s.store_id = st.store_id
WHERE 
    LOWER(b.brand_name) LIKE '%sun%bicycle%'
GROUP BY 
    st.store_name
ORDER BY 
    total_stock ASC
LIMIT 1;

Conversation history:
User: Show me the active staff members.
AI: SELECT staff_id, first_name, last_name, email, phone, active, store_id, manager_id FROM staffs WHERE active = 1;

Last line:
User: Identify employees who have processed the most orders in the last 12 months.
Output:
SELECT 
    s.first_name, 
    s.last_name, 
    COUNT(o.order_id) AS total_orders 
FROM 
    staffs s 
JOIN 
    orders o ON s.staff_id = o.staff_id 
WHERE 
    o.order_date > (CURRENT_DATE - INTERVAL '1 YEAR') 
GROUP BY 
    s.staff_id, s.first_name, s.last_name 
ORDER BY 
    total_orders DESC 
LIMIT 1;

Conversation history:
User: Show me the active staff members.
AI: SELECT staff_id, first_name, last_name, email, phone, active, store_id, manager_id FROM staffs WHERE active = 1;

Last line:
User: Get the total number of orders placed in each store.

Output:
WITH StoreOrders AS (
    SELECT Store_id, COUNT(Order_id) AS Total_Orders
    FROM orders
    GROUP BY Store_id
)
SELECT s.Store_name, so.Total_Orders
FROM StoreOrders so
JOIN stores s ON so.Store_id = s.Store_id;

Conversation history (for reference only):
{history}
Last line of conversation (for extraction):
User: {input}

Context:
{entities}

Current conversation:

Last line:
Human: {input}

You:
"""

_DEFAULT_ENTITY_MEMORY_CONVERSATION_TEMPLATE = """{final_output}"""

Prompt_template=_DEFAULT_ENTITY_MEMORY_CONVERSATION_TEMPLATE.format(final_output=final_output)

ENTITY_MEMORY_CONVERSATION_TEMPLATE1 = PromptTemplate(
    input_variables=["entities","history","input"],
    template=Prompt_template,
)



# from langchain_core.prompts.prompt import PromptTemplate
# from savedex import final_output

# # Define the default conversation template
# _DEFAULT_ENTITY_MEMORY_CONVERSATION_TEMPLATE = """{final_output}"""

# # Format the template with the imported `final_output`

# Prompt_template=_DEFAULT_ENTITY_MEMORY_CONVERSATION_TEMPLATE.format(final_output=final_output)

# # Create the PromptTemplate object
# ENTITY_MEMORY_CONVERSATION_TEMPLATE1 = PromptTemplate(
#     input_variables=["entities","history","input"],  # Include variables provided by memory
#     template=Prompt_template,
# )
