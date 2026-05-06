# 출석 명단을 담을 바구니
students = []

print("학생 이름을 입력하세요 (다 입력했으면 '끝'이라고 입력)")

while True:
    name = input("이름: ")
    if name == "끝":
        break
    students.append(name)

print("-" * 20)
print(f"오늘 총 {len(students)}명이 왔어요!")
print("명단:", students)