import pymysql as pms
from getpass import getpass
from db_connection import db_connect

Admin_idx = None


def admin_page():
    while True:
        print("=" * 50)
        print("관리자 페이지".center(45))
        print("=" * 50)
        print("1. 회원가입")
        print("2. 로그인")
        print("3. 뒤로가기")
        choice = input("선택: ")
        print("\n\n")

        if choice == "1":
            admin_signup()
        elif choice == "2":
            admin_login()
        elif choice == "3":
            print("메인 메뉴로 돌아갑니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")


def is_adminid_duplicate(adminid):
    connection = db_connect()
    cursor = connection.cursor()
    try:
        query = "SELECT COUNT(*) FROM ADMIN WHERE Aid = %s"
        cursor.execute(query, (adminid,))
        result = cursor.fetchone()

        if (result[0] == 0):
            return False
        return True

    except Exception as e:
        print("is adminid duplicate err")
        return True

    finally:
        cursor.close()
        connection.close()


def admin_signup():
    connection = db_connect()
    cursor = connection.cursor()
    print("=" * 50)
    print("관리자 회원가입".center(45))
    print("=" * 50)

    while True:
        adminid = input("관리자 ID를 입력하세요(10자 이내): ")
        if (is_adminid_duplicate(adminid)):
            print("이미 존재하는 ID입니다. 다른 ID를 입력하세요.\n")
            continue
        break
    Aname = input("관리자 이름을 입력하세요 (10자 이내): ")
    Apwd = getpass("비밀번호를 입력하세요(20자 이내): ")

    try:
        query = "INSERT INTO ADMIN (Aid, Aname, Apwd) VALUES (%s, %s, %s)"
        cursor.execute(query, (adminid, Aname, Apwd))
        connection.commit()
        print("회원가입이 성공적으로 완료되었습니다.\n\n")

    except pms.IntegrityError as e:
        print(f"admin signup err: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def admin_login():
    global Admin_idx

    connection = db_connect()
    cursor = connection.cursor()
    print("=" * 50)
    print("관리자 로그인".center(45))
    print("=" * 50)
    Aid = input("ID를 입력하세요: ")
    Apwd = getpass("비밀번호를 입력하세요: ")

    try:
        query = "SELECT * FROM ADMIN WHERE Aid = %s AND Apwd = %s"
        cursor.execute(query, (Aid, Apwd))
        result = cursor.fetchone()

        if result:
            print(f"로그인 성공! 안녕하세요, {result[2]}님.\n\n")
            Admin_idx = result[0]

            while True:
                print("=" * 50)
                print("관리자 대시보드".center(45))
                print("=" * 50)
                print("0. 가수 등록")
                print("1. 앨범 및 음악 등록")
                print("2. 앨범 삭제")
                print("3. 음악 삭제")
                print("4. 관리 중인 앨범 보기")
                print("5. 로그아웃")
                print("=" * 50)
                choice = input("선택: ")
                print("\n\n")

                if choice == "0":
                    artist_registration()
                elif choice == "1":
                    album_registration()
                elif choice == "2":
                    delete_album()
                elif choice == "3":
                    delete_music()
                elif choice == "4":
                    view_managed_albums()
                elif choice == "5":
                    print("로그아웃합니다.")
                    break
                else:
                    print("올바른 번호를 입력하세요.")
        else:
            print("ID 또는 비밀번호가 올바르지 않습니다.")
    except pms.Error as e:
        print(f"admin_login err: {e}")
    finally:
        cursor.close()
        connection.close()


def get_artist_idx(artist_name):
    connection = db_connect()
    cursor = connection.cursor()
    try:
        query = "SELECT Artist_idx FROM ARTIST WHERE Artist_name = %s"
        cursor.execute(query, (artist_name,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            print(f"가수 '{artist_name}'을(를) 찾을 수 없습니다.")
            return None
    except Exception as e:
        print(f"get_artist_idx err: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def album_registration():
    print("=" * 50)
    print("노래 등록 페이지".center(45))
    print("=" * 50)

    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print("앨범 등록".center(45))
        print("=" * 50)

        Album_name = input("앨범 이름: ")
        Description = input("앨범 설명: ")
        Release_date = input("앨범 출시일 (YYYY-MM-DD): ")
        Owner_artist_name = input("앨범 소유 가수: ")
        Owner_artist_idx = get_artist_idx(Owner_artist_name)

        query = """
            INSERT INTO ALBUM (Album_name, Description, Release_date, Admin_idx, Owner_artist_idx)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (Album_name, Description,
                       Release_date, Admin_idx, Owner_artist_idx))
        connection.commit()
        print("앨범이 성공적으로 등록되었습니다.\n\n")

        cursor.execute("SELECT LAST_INSERT_ID();")
        Album_idx = cursor.fetchone()[0]
        music_registration(Album_idx)
        set_title(Album_idx)

    except pms.Error as e:
        print(f"album registration err: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def music_registration(Album_idx):
    print("=" * 50)
    print("노래 등록".center(45))
    print("=" * 50)
    connection = db_connect()
    cursor = connection.cursor()
    try:
        while True:
            name = input("노래 제목: ")
            Duration = input("재생 시간 (HH:MM:SS): ")
            Lyrics = input("가사 (가사가 없다면 Enter): ") or None
            Genre = input("장르: ")
            Likes_cnt = 0
            Streaming_cnt = 0

            query = """
                INSERT INTO MUSIC (Music_name, Duration, Lyrics, Genre, Likes_cnt, Streaming_cnt, Inc_Album_idx)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(query, (name, Duration, Lyrics, Genre,
                           Likes_cnt, Streaming_cnt, Album_idx))
            connection.commit()
            print(f"노래 '{name}'이(가) 성공적으로 등록되었습니다.\n\n")

            cursor.execute("SELECT LAST_INSERT_ID();")
            Music_idx = cursor.fetchone()[0]

            print("=" * 50)
            print("가수 등록".center(45))
            print("=" * 50)
            added_artist = False

            while True:
                artist_name = input("가수 이름 (끝내려면 Enter): ")

                if not artist_name:
                    if not added_artist:
                        print("적어도 한 명의 가수를 추가해야 합니다.")
                        continue
                    break

                artist_idx = get_artist_idx(artist_name)

                if artist_idx is None:
                    print(f"가수 '{artist_name}'이(가) 없습니다. 추가 후 다시 시도하세요.\n")
                    continue

                query_singer = """
                    INSERT INTO SINGERS (Music_idx, Singer_idx)
                    VALUES (%s, %s)
                """
                cursor.execute(query_singer, (Music_idx, artist_idx))
                connection.commit()
                added_artist = True
                print(f"가수 '{artist_name}'이(가) 등록되었습니다.\n")

            print("=" * 50)
            print("작곡가 등록".center(45))
            print("=" * 50)
            while True:
                Composer_name = input("작곡가 이름 (없다면 Enter): ")
                if not Composer_name:
                    break
                query_composer = """
                    INSERT INTO COMPOSER (Music_idx, Composer_name)
                    VALUES (%s, %s)
                """
                cursor.execute(query_composer, (Music_idx, Composer_name))
                connection.commit()
                print(f"작곡가 '{Composer_name}'이(가) 등록되었습니다.\n")

            print("=" * 50)
            print("작사가 등록".center(45))
            print("=" * 50)
            while True:
                Lyricist_name = input("작사가 이름 (없다면 Enter): ")
                if not Lyricist_name:
                    break
                query_lyricist = """
                    INSERT INTO LYRICIST (Music_idx, Lyricist_name)
                    VALUES (%s, %s)
                """
                cursor.execute(query_lyricist, (Music_idx, Lyricist_name))
                connection.commit()
                print(f"작사가 '{Lyricist_name}'이(가) 등록되었습니다.\n")

            more_songs = input("다른 노래를 추가하시겠습니까? (y/n): ")
            if more_songs != 'y':
                break

    except pms.Error as e:
        print(f"album registration err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def set_title(Album_idx):
    print("=" * 50)
    print("타이틀 곡 등록".center(45))
    print("=" * 50)

    connection = db_connect()
    cursor = connection.cursor()

    try:
        Music_name = input("타이틀 곡 이름 (없으면 Enter): ").strip()

        if not Music_name:
            print("타이틀 곡이 설정되지 않았습니다.\n")
            return

        cursor.execute("""
            SELECT Music_idx 
            FROM MUSIC 
            WHERE Music_name = %s AND Inc_Album_idx = %s
        """, (Music_name, Album_idx))

        result = cursor.fetchone()

        if result:
            Music_idx = result[0]

            query = """
                INSERT INTO TITLESONG (Album_idx, Music_idx)
                VALUES (%s, %s)
            """
            cursor.execute(query, (Album_idx, Music_idx))
            connection.commit()
            print(f"타이틀 곡 '{Music_name}'이(가) 성공적으로 등록되었습니다.\n")
        else:
            print(f"'{Music_name}'이(가) 존재하지 않습니다.")

    except pms.Error as e:
        print(f"title registration err: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def delete_album():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        album_name = input("\n삭제할 앨범 이름을 입력하세요: ")

        query = """
            SELECT Album_idx
            FROM ALBUM 
            WHERE Album_name LIKE %s AND Admin_idx = %s
        """
        cursor.execute(query, (album_name, Admin_idx))
        result = cursor.fetchone()

        if not result:
            print(f"'{album_name}' 이름의 앨범을 찾을 수 없습니다.")
            return

        album_idx = result[0]

        query = "DELETE FROM ALBUM WHERE Album_idx = %s AND Admin_idx = %s"
        cursor.execute(query, (album_idx, Admin_idx))
        connection.commit()
        print(f"{album_name} 앨범이 성공적으로 삭제되었습니다.\n")

    except pms.Error as e:
        print(f"delete_album err: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def delete_music():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        album_name = input("\n음악을 삭제할 앨범 이름을 입력하세요: ")

        query = """
            SELECT Album_idx 
            FROM ALBUM 
            WHERE Album_name = %s AND Admin_idx = %s
        """
        cursor.execute(query, (album_name, Admin_idx))
        result = cursor.fetchone()

        if not result:
            print(f"'{album_name}' 이름의 앨범을 찾을 수 없습니다.\n")
            return

        album_idx = result[0]

        query = """
            SELECT Music_idx, Music_name 
            FROM MUSIC 
            WHERE Inc_Album_idx = %s
        """
        cursor.execute(query, (album_idx,))
        music_list = cursor.fetchall()

        if not music_list:
            print(f"앨범 '{album_name}'에 포함된 음악이 없습니다.\n")
            return

        print("=" * 50)
        print("음악 목록".center(45))
        print("=" * 50)

        for music in music_list:
            print(f"{music[1]}")

        music_name = input("\n삭제할 음악 이름을 입력하세요: ")
        query_delete = """
            DELETE FROM MUSIC 
            WHERE Music_name = %s AND Inc_Album_idx = %s
        """
        cursor.execute(query_delete, (music_name, album_idx))
        connection.commit()

        if cursor.rowcount > 0:
            print(f"음악 '{music_name}'이(가) 성공적으로 삭제되었습니다.\n")
        else:
            print(f"음악 '{music_name}'을(를) 찾을 수 없습니다.\n")

    except pms.Error as e:
        print(f"delete_music err {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def view_managed_albums():

    print("=" * 50)
    print("관리 중인 앨범".center(45))
    print("=" * 50)
    connection = db_connect()
    cursor = connection.cursor()
    try:
        query = """
            SELECT Album_idx, Album_name, Description, Release_date, Owner_artist_idx
            FROM ALBUM
            WHERE Admin_idx = %s
        """
        cursor.execute(query, (Admin_idx,))
        albums = cursor.fetchall()

        if albums:
            print("=" * 50)
            print("관리 중인 앨범 목록".center(45))
            print("=" * 50)

            for album in albums:
                album_idx = album[0]
                album_name = album[1]
                description = album[2]
                release_date = album[3]
                owner_artist_idx = album[4]

                query = """
                    SELECT Artist_name 
                    FROM ARTIST 
                    WHERE Artist_idx = %s
                """
                cursor.execute(query, (owner_artist_idx,))
                owner_artist = cursor.fetchone()
                owner_artist_name = owner_artist[0]

                print(f"앨범 이름: {album_name}")
                print(f"앨범 설명: {description}")
                print(f"출시일: {release_date}")
                print(f"소유 가수: {owner_artist_name}")

                query = """
                    SELECT MUSIC.Music_idx, MUSIC.Music_name, MUSIC.Duration, MUSIC.Genre 
                    FROM TITLESONG 
                    JOIN MUSIC ON TITLESONG.Music_idx = MUSIC.Music_idx 
                    WHERE TITLESONG.Album_idx = %s
                """
                cursor.execute(query, (album_idx,))
                title_songs = cursor.fetchall()

                if title_songs:
                    print("\n타이틀 곡:")
                    for title_song in title_songs:
                        print(
                            f"  > 제목: {title_song[1]}, 재생 시간: {title_song[2]}, 장르: {title_song[3]}")
                else:
                    print("\n타이틀 곡 정보가 없습니다.")

                query = """
                    SELECT MUSIC.Music_idx, MUSIC.Music_name, MUSIC.Duration, MUSIC.Genre 
                    FROM MUSIC 
                    WHERE Inc_Album_idx = %s
                """
                cursor.execute(query, (album_idx,))
                songs = cursor.fetchall()

                if songs:
                    print("\n앨범에 포함된 노래:")
                    for song in songs:
                        music_idx = song[0]
                        music_name = song[1]
                        duration = song[2]
                        genre = song[3]

                        query = """
                            SELECT ARTIST.Artist_name 
                            FROM SINGERS 
                            JOIN ARTIST ON SINGERS.Singer_idx = ARTIST.Artist_idx 
                            WHERE SINGERS.Music_idx = %s
                        """
                        cursor.execute(query, (music_idx,))
                        participating_artists = cursor.fetchall()
                        artist_names = [artist[0]
                                        for artist in participating_artists]

                        print(
                            f"  > 제목: {music_name}, 재생 시간: {duration}, 장르: {genre}")
                        if artist_names:
                            print(f"    참여 가수: {', '.join(artist_names)}")
                        else:
                            print("    참여 가수 정보가 없습니다.")
                else:
                    print("\n앨범에 포함된 노래가 없습니다.")
                print("=" * 50)
            print("=" * 50)
        else:
            print("관리 중인 앨범이 없습니다.\n")

    except pms.Error as e:
        print(f"view_managed_albums err: {e}")
    finally:
        cursor.close()
        connection.close()


def artist_registration():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print("가수 등록".center(50))
        print("=" * 50)

        artist_name = input("등록할 가수 이름을 입력하세요: ")
        info = input("가수 정보를 입력하세요 (없으면 Enter): ")

        query = "SELECT COUNT(*) FROM ARTIST WHERE Artist_name = %s"
        cursor.execute(query, (artist_name,))
        result = cursor.fetchone()

        if result[0] > 0:
            print(f"'{artist_name}' 이름의 가수는 이미 등록되어 있습니다.")
            return

        query = """
            INSERT INTO ARTIST (Artist_name, Info)
            VALUES (%s, %s)
        """
        cursor.execute(query, (artist_name, info if info else None))
        connection.commit()

        print(f"가수 '{artist_name}'가 성공적으로 등록되었습니다!")

    except Exception as e:
        print(f"artist_registration err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()
