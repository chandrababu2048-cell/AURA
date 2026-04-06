print("---Part1 : simple Dictionary Test---")
user = {
     "name": "Chandu",
     "ai_name": "Jarvis",
     "wake_time": "7:00"
 }
print(user["name"])
print(user["ai_name"])
print(user["wake_time"])

#part2 : nested dictionary"

print("\n--- Part 2: nested Dictionary ----")

response = {
    "status": "success",
    "DATA":{
        "user": "Chandu",
    "message": "hello from aura !"
    }
}

message = response["DATA"]["message"]
print(message)

print("\n --- Part 3: dictionary with list ---")

claude_response = {
    "id": "msg_123",
    "type":"message",
    "content" : [{
        "type": "text",
        "text": "good morning Chandu ! you have 3 plans today"

    }]

}

content = claude_response["content"]
print(f"content: {content}")

first_item = content[0]
print(f"first item: {first_item}")

actual_item = first_item["text"]
print(f"actual item: {actual_item}")

text = claude_response["content"][0]["text"]
print(f"text: {text}")

print(f"one line :{text}")


print("\n ---- part 4: list of dictionaries ----")

plans = [
    {"id":1 , "plan_text": "finish brain.py ",  "is_done": 0},
    {"id":2 , "plan_text":"practice leetcode", "is_done": 1},
    {"id":3, "plan_text" : "push to github", "is_done": 0}

]

for plan in plans:
    status = "success" if plan ["is_done"] else "loading"
    print(f"{status} {plan['plan_text']}")
