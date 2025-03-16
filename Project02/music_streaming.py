from admin import admin_page
from user import user_page


def main():
    while True:
        print("=" * 50)
        print("music streaming".center(45))
        print("=" * 50)
        print("1. 관리자 시스템")
        print("2. 사용자 시스템")
        print("3. 종료")
        choice = input("선택: ")
        if choice == "1":
            admin_page()
        elif choice == "2":
            user_page()
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")


if __name__ == "__main__":
    main()
