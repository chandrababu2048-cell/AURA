print("---Test 1: Division")
try:
    result = 10/0
    print(f"result is {result}")
except Exception as e:
    print(f"something went wrong: {e}")
print("program is still running")

print("\n ----test 2: Wrong dictionary key ---")

try:
    user = {"name" : "chandu", "age": 25}
    print(user["salary"])
except Exception as e:
    print(f"something went wrong: {e}")
print("program is still running")

print("\n ----test 3: API simulation ---")
def fake_api_call(should_fail):
    if should_fail:
        raise  Exception("API timeout! Server busy.")
    return "hello from claude!"

try:
    response = fake_api_call(should_fail=True)
    print(f"API said : {response}")

except Exception as e:
    print(f"API failed : {e}")
    print("using backup response instead!")

print("program is still running")

print("\n ----test 4: Successfully API----")


try:
    response = fake_api_call(should_fail = False)
    print(f"API said : {response}")
except Exception as e:
    print(f"API failed : {e}")
print("done")


