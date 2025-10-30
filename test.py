def test_function():
    print("This is a test function.")
    
def test_function_a():
    print("This is a test function.")
    
def test_function_b():
    print("This is a test function.")

# 1234

# Update Gemini API request to include API key in headers; adjust JSON structure for prompt

 
 



# def parse_gemini_json_2(response):
#     import re, json 
#     text = response
#     text = re.sub(r"^```[a-zA-Z]*\n?|```$", "", text.strip())
#     return json.loads(text)

# m = "{\"valid\": false, \"errors\": [{\"line\": 1, \"message\": \"Unexpected indentation. Function definition should not have leading spaces at the module level.\"}]}"
# print(parse_gemini_json_2(m))

# a = {
#     'valid': False, 
#     'errors': [
#         {
#             'line': 1, 
#             'message': 'Unexpected indentation. Function definition should not have leading spaces at the module level.'
#         }
#     ]
# }