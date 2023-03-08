dragdrop = [{"id": 3, "text": "apple"}, {"id": 1, "text": "I"}, {"id": 2, "text": "like"}]


correct_answer = [x["id"] for x in dragdrop]
correct_answer.sort()
print(correct_answer)
