import pymysql as pms
from getpass import getpass
from db_connection import db_connect
import time
import sys


class UserInfo:
    def __init__(self, Uidx, Uid, Uname, Uemail, Join_date):
        self.Uidx = Uidx
        self.Uid = Uid
        self.Uname = Uname
        self.Uemail = Uemail
        self.Join_date = Join_date


user_info = None


def user_page():
    while True:
        print("=" * 50)
        print("사용자 페이지".center(45))
        print("=" * 50)
        print("1. 회원가입")
        print("2. 로그인")
        print("3. 뒤로가기")
        print("=" * 50)
        choice = input("선택: ")
        print("\n\n")

        if choice == "1":
            user_signup()
        elif choice == "2":
            user_login()
        elif choice == "3":
            print("메인 메뉴로 돌아갑니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")


def is_userid_duplicate(userid):
    connection = db_connect()
    cursor = connection.cursor()
    try:
        query = "SELECT COUNT(*) FROM USER WHERE Uid = %s"
        cursor.execute(query, (userid,))
        result = cursor.fetchone()

        if (result[0] == 0):
            return False
        return True

    except Exception as e:
        print("is userid duplicate err")
        return True

    finally:
        cursor.close()
        connection.close()


def user_signup():
    connection = db_connect()
    cursor = connection.cursor()

    print("=== 사용자 회원가입 ===")

    while True:
        userid = input("사용자 ID를 입력하세요(10자 이내): ")
        if (is_userid_duplicate(userid)):
            print("이미 존재하는 ID입니다. 다른 ID를 입력하세요.")
            continue
        break

    username = input("사용자 이름을 입력하세요(10자 이내): ")
    useremail = input("사용자 이메일을 입력하세요(50자 이내): ")
    userpwd = getpass("비밀번호를 입력하세요(20자 이내): ")

    try:
        query = "INSERT INTO USER (Uid, Uname, Uemail, Upwd, Join_date) VALUES (%s, %s, %s, %s, CURRENT_DATE)"
        cursor.execute(query, (userid, username, useremail, userpwd))
        connection.commit()
        print("회원가입이 완료되었습니다.")

    except Exception as e:
        print(f"user signup err: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def user_login():
    global user_info

    connection = db_connect()
    cursor = connection.cursor()

    print("=" * 50)
    print("사용자 로그인".center(45))
    print("=" * 50)
    userid = input("ID: ")
    userpwd = getpass("PWD: ")
    print("\n\n")

    try:
        query = "SELECT * FROM USER WHERE Uid = %s AND Upwd = %s"
        cursor.execute(query, (userid, userpwd))
        result = cursor.fetchone()
        if result:
            user_info = UserInfo(
                Uidx=result[0],
                Uid=result[1],
                Uname=result[2],
                Uemail=result[3],
                Join_date=result[5]
            )
            print("로그인 성공!")
            print(f"환영합니다, {user_info.Uname}님.\n\n")
            user_dashboard()
        else:
            print("\n로그인 실패: ID 또는 비밀번호가 잘못되었습니다.\n\n")

    except Exception as e:
        print(f"\nerr: {e}")

    finally:
        cursor.close()
        connection.close()


def user_dashboard():
    while True:
        print("=" * 50)
        print("사용자 대시보드".center(43))
        print("=" * 50)
        print("1. 노래 검색")
        print("2. 플레이리스트 생성")
        print("3. 보유 중인 플레이리스트 보기")
        print("4. 플레이리스트 수정")
        print("5. 플레이리스트 삭제")
        print("6. 다른 사람의 플레이리스트 보기")
        print("7. 가수 검색")
        print("8. 좋아요 한 음악 보기")
        print("9. 좋아요 한 가수 보기")
        print("10. 가장 많이 스트리밍 된 음악 top 5")
        print("11. 가장 좋아요가 많은 음악 top 5")
        print("0. 로그아웃")
        print("=" * 50)
        choice = input("원하는 작업을 선택하세요: ")
        print("\n\n\n")

        if choice == "1":
            search_song()
        elif choice == "2":
            create_playlist()
        elif choice == "3":
            view_playlists()
        elif choice == "4":
            edit_playlist()
        elif choice == "5":
            delete_playlist()
        elif choice == "6":
            view_all_playlists()
        elif choice == "7":
            search_artist()
        elif choice == "8":
            view_like_music()
        elif choice == "9":
            view_like_artist()
        elif choice == "10":
            top_streaming_musics()
        elif choice == "11":
            top_liked_musics()
        elif choice == "0":
            print("로그아웃합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")


def search_song():
    while True:
        print("=" * 50)
        print("노래 검색".center(40))
        print("=" * 50)
        print("1. 노래 제목으로 검색")
        print("2. 가수로 검색")
        print("3. 장르로 검색")
        print("4. 뒤로가기")
        print("=" * 50)
        choice = input("선택: ")
        print("\n\n")

        if choice == "1":
            search_by_name()
        elif choice == "2":
            search_by_artist()
        elif choice == "3":
            search_by_genre()
        elif choice == "4":
            print("노래 검색을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")


def search_by_name():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        name = input("검색할 노래 제목을 입력하세요: ")
        query = """
            SELECT Music_idx, Music_name, Duration, Genre, Lyrics
            FROM MUSIC 
            WHERE Music_name LIKE %s 
        """

        cursor.execute(query, (f"%{name}%",))
        musics = cursor.fetchall()

        if musics:
            playing(musics)
        else:
            print(f"'{name}' 제목을 포함하는 노래가 없습니다.")

    except Exception as e:
        print(f"search_by_name err: {e}")

    finally:
        cursor.close()
        connection.close()


def search_by_artist():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        artist_name = input("\n검색할 가수 이름을 입력하세요: ")
        query = """
            SELECT MUSIC.Music_idx, Music_name, Duration, Genre, Lyrics
            FROM ARTIST
            JOIN SINGERS ON Artist_idx = Singer_idx
            JOIN MUSIC ON SINGERS.Music_idx = MUSIC.Music_idx
            WHERE ARTIST.Artist_name LIKE %s;
        """
        cursor.execute(query, (f"%{artist_name}%",))
        musics = cursor.fetchall()

        if musics:
            playing(musics)
        else:
            print(f"'{artist_name}' 가수의 노래가 없습니다.")

    except Exception as e:
        print(f"search by artist err: {e}")

    finally:
        cursor.close()
        connection.close()


def search_by_genre():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        genre = input("검색할 장르를 입력하세요: ")
        query = """
            SELECT Music_idx, Music_name, Duration, Genre, Lyrics
            FROM MUSIC 
            WHERE Genre = %s
        """
        cursor.execute(query, (genre,))
        musics = cursor.fetchall()

        if musics:
            playing(musics)

        else:
            print(f"'{genre}' 장르의 노래가 없습니다.")

    except Exception as e:
        print(f"search_by_genre err: {e}")

    finally:
        cursor.close()
        connection.close()


def playing(musics):
    print("=" * 50)
    print(" 검색 결과 ".center(50))
    print("=" * 50)

    for idx, music in enumerate(musics, start=1):
        connection = db_connect()
        cursor = connection.cursor()
        try:
            query = """
                SELECT ARTIST.Artist_name
                FROM SINGERS
                JOIN ARTIST ON SINGERS.Singer_idx = ARTIST.Artist_idx
                WHERE SINGERS.Music_idx = %s
            """
            cursor.execute(query, (music[0],))
            singers = cursor.fetchall()
            singer_names = ", ".join(singer[0] for singer in singers)
        except Exception as e:
            singer_names = "알 수 없음"
            print(f"playing err: {e}")
        finally:
            cursor.close()
            connection.close()

        print(f"{idx}. 제목: {music[1]}, 재생 시간: {music[2]}, 장르: {music[3]}")
        print(f"    - 가수: {singer_names} ")

    print("=" * 50 + "\n\n")

    print("=" * 50)
    print("무엇을 하시겠습니까?")
    print("1. 노래 재생")
    print("2. 좋아하는 음악에 추가")
    print("=" * 50)

    action = int(input("원하는 작업을 선택하세요 (뒤로가기: 0): "))
    print("\n")

    if action == 0:
        print("작업을 취소했습니다.")
        return
    elif action not in [1, 2]:
        print("잘못된 작업 선택입니다.")
        return

    if action == 1:
        prompt = "재생할 노래 번호를 선택하세요 (뒤로가기: 0): "
    elif action == 2:
        prompt = "좋아하는 음악에 추가할 음악 번호를 선택하세요 (뒤로가기: 0): "

    song_choice = int(input(prompt))
    print("\n")

    if song_choice == 0:
        print("작업을 취소했습니다.")
        return

    elif 1 <= song_choice <= len(musics):
        selected_music = musics[song_choice - 1]
        if action == 1:
            play_music(selected_music)
        elif action == 2:
            add_to_like_music(selected_music)
    else:
        print("잘못된 번호입니다.")


def play_music(music):
    print("\n" + "=" * 50)
    print("재생중...".center(45))
    print("=" * 50)
    print(f"제목: {music[1]}")
    print(f"재생시간: {music[2]}")
    print(f"장르: {music[3]}")
    print(f"가사:")
    print(f"{music[4]}")
    print("\n\n")
    update_streaming_cnt(music)


def update_streaming_cnt(music):
    connection = db_connect()
    cursor = connection.cursor()
    try:
        query = """
            UPDATE MUSIC 
            SET Streaming_cnt = Streaming_cnt + 1
            WHERE Music_idx = %s
        """
        cursor.execute(query, (music[0],))
        connection.commit()

    except Exception as e:
        print(f"update_streaming_cnt err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def add_to_like_music(music):
    connection = db_connect()
    cursor = connection.cursor()

    try:

        query = """
            SELECT COUNT(*) 
            FROM LIKE_MUSIC
            WHERE User_idx = %s AND Music_idx = %s
        """
        cursor.execute(query, (user_info.Uidx, music[0]))
        already_like = cursor.fetchone()[0]

        if already_like:
            print("이미 좋아하는 음악 목록에 있습니다.")
            return

        query = """
            INSERT INTO LIKE_MUSIC (User_idx, Music_idx)
            VALUES (%s, %s)
        """
        cursor.execute(query, (user_info.Uidx, music[0]))
        connection.commit()
        print("선택한 노래가 좋아하는 음악에 추가되었습니다.")
        update_likes_cnt(music)

    except Exception as e:
        print(f"add_to_like_music err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def update_likes_cnt(music):
    connection = db_connect()
    cursor = connection.cursor()
    try:
        query = """
            UPDATE MUSIC 
            SET Likes_cnt = Likes_cnt + 1
            WHERE Music_idx = %s
        """
        cursor.execute(query, (music[0],))
        connection.commit()

    except Exception as e:
        print(f"update_likes_cnt err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def create_playlist():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print("플레이리스트 생성".center(45))
        print("=" * 50)
        playlist_name = input("플레이리스트 이름을 입력하세요: ")
        print("\n")

        query = """
            INSERT INTO PLAYLIST (Playlist_name, Owner_user_idx)
            VALUES (%s, %s)
        """
        cursor.execute(query, (playlist_name, user_info.Uidx))
        connection.commit()

        query = "SELECT LAST_INSERT_ID()"
        cursor.execute(query)
        playlist_id = cursor.fetchone()[0]
        print(f"'{playlist_name}' 플레이리스트가 생성되었습니다.")

        print("\n노래를 플레이리스트에 추가합니다.")
        add_music_to_playlist(playlist_id, cursor)

        print("플레이리스트 생성 및 노래 추가가 완료되었습니다.")

    except Exception as e:
        print(f"create_playlist err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def view_playlists():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("\n" + "=" * 50)
        print("보유 중인 플레이리스트.".center(40))
        print("=" * 50)
        query = """
            SELECT Playlist_idx, Playlist_name 
            FROM PLAYLIST 
            WHERE Owner_user_idx = %s
        """
        cursor.execute(query, (user_info.Uidx,))
        playlists = cursor.fetchall()

        if not playlists:
            print("현재 보유 중인 플레이리스트가 없습니다.")
            return

        for playlist in playlists:
            playlist_id, playlist_name = playlist
            print(f"\n플레이리스트 이름: {playlist_name}")

            query = """
                SELECT MUSIC.Music_name, MUSIC.Duration, MUSIC.Genre 
                FROM PLAYLIST_MUSIC 
                JOIN MUSIC ON PLAYLIST_MUSIC.Music_idx = MUSIC.Music_idx 
                WHERE PLAYLIST_MUSIC.Play_idx = %s
            """
            cursor.execute(query, (playlist_id,))
            songs = cursor.fetchall()

            if songs:
                print("포함된 노래:")
                for song in songs:
                    print(
                        f"  > 제목: {song[0]}")
            else:
                print("이 플레이리스트에는 노래가 없습니다.")
            print("=" * 50)

    except Exception as e:
        print(f"view_playlists err: {e}")

    finally:
        cursor.close()
        connection.close()


def edit_playlist():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print("내 플레이리스트".center(46))
        print("=" * 50)

        query = """
            SELECT Playlist_idx, Playlist_name
            FROM PLAYLIST
            WHERE Owner_user_idx = %s
        """
        cursor.execute(query, (user_info.Uidx,))
        playlists = cursor.fetchall()

        if not playlists:
            print("현재 보유 중인 플레이리스트가 없습니다.")
            return

        for idx, playlist in enumerate(playlists, start=1):
            print(f"{idx}. {playlist[1]}")
        print("=" * 50)

        while True:
            try:
                choice = int(input("수정할 플레이리스트 번호를 선택하세요 (뒤로가기: 0): "))
                if choice == 0:
                    print("플레이리스트 수정을 취소합니다.")
                    return
                elif 1 <= choice <= len(playlists):
                    selected_playlist = playlists[choice - 1]
                    playlist_idx, playlist_name = selected_playlist
                    print(f"\n'{playlist_name}' 플레이리스트를 선택하셨습니다.\n")
                    break
                else:
                    print("유효한 번호를 입력하세요.")
            except ValueError:
                print("숫자를 입력하세요.")

        print("=" * 50)
        print(f"'{playlist_name}' 플레이리스트의 노래 목록".center(10))
        print("=" * 50)

        query_songs = """
            SELECT MUSIC.Music_name, MUSIC.Duration, MUSIC.Genre 
            FROM PLAYLIST_MUSIC 
            JOIN MUSIC ON PLAYLIST_MUSIC.Music_idx = MUSIC.Music_idx 
            WHERE PLAYLIST_MUSIC.Play_idx = %s
        """
        cursor.execute(query_songs, (playlist_idx,))
        songs = cursor.fetchall()

        if songs:
            for idx, song in enumerate(songs, start=1):
                print(f"{idx}. 제목: {song[0]}, 재생 시간: {song[1]}, 장르: {song[2]}")
        else:
            print("이 플레이리스트에는 현재 노래가 없습니다.")
        print("=" * 50)
        print("\n")

        while True:
            print("=" * 50)
            print("작업 선택".center(40))
            print("1. 노래 추가")
            print("2. 노래 삭제")
            print("3. 돌아가기")
            print("=" * 50)
            choice = input("선택: ")
            print("\n")

            if choice == "1":
                add_music_to_playlist(playlist_idx, cursor)
            elif choice == "2":
                delete_music_from_playlist(playlist_idx, cursor)
            elif choice == "3":
                print("플레이리스트 수정을 종료합니다.")
                break
            else:
                print("잘못된 입력입니다. 다시 선택하세요.")

    except Exception as e:
        print(f"edit_playlist err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def add_music_to_playlist(playlist_idx, cursor):
    connection = db_connect()
    cursor = connection.cursor()
    try:
        while True:
            song_name = input("추가할 노래 제목을 입력하세요 (종료하려면 Enter): ")
            if not song_name:
                print("노래 추가를 종료합니다.\n")
                break

            query = """
                SELECT Music_idx, Music_name, Duration, Genre
                FROM MUSIC 
                WHERE Music_name LIKE %s 
            """
            cursor.execute(query, (f"%{song_name}%",))
            musics = cursor.fetchall()

            if musics:
                print("=" * 50)
                print(" 검색 결과 ".center(50))
                print("=" * 50)

                for idx, music in enumerate(musics, start=1):
                    try:

                        query_singers = """
                            SELECT ARTIST.Artist_name
                            FROM SINGERS
                            JOIN ARTIST ON SINGERS.Singer_idx = ARTIST.Artist_idx
                            WHERE SINGERS.Music_idx = %s
                        """
                        cursor.execute(query_singers, (music[0],))
                        singers = cursor.fetchall()
                        singer_names = ", ".join(
                            singer[0] for singer in singers)
                    except Exception as e:
                        singer_names = "알 수 없음"
                        print(f"가수 정보 로드 에러: {e}")

                    print(
                        f"{idx}. 제목: {music[1]}, 재생 시간: {music[2]}, 장르: {music[3]}")
                    print(f"    - 가수: {singer_names}")

                print("=" * 50)

                while True:
                    try:

                        choice = int(input("추가할 노래 번호를 선택하세요 (취소: 0): "))
                        print("\n")
                        if choice == 0:
                            print("노래 추가를 취소합니다.")
                            break
                        elif 1 <= choice <= len(musics):
                            selected_music = musics[choice - 1]

                            query = "INSERT INTO PLAYLIST_MUSIC (Play_idx, Music_idx) VALUES (%s, %s)"
                            cursor.execute(
                                query, (playlist_idx, selected_music[0]))
                            connection.commit()
                            print(
                                f"'{selected_music[1]}' 노래가 플레이리스트에 추가되었습니다.\n\n")
                            break
                        else:
                            print("유효한 번호를 입력하세요.")
                    except ValueError:
                        print("숫자를 입력하세요.")
            else:
                print(f"'{song_name}' 제목의 노래는 존재하지 않습니다. 다시 시도하세요.")

    except Exception as e:
        print(f"add_music_to_playlist err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def delete_music_from_playlist(playlist_idx, cursor):
    connection = db_connect()
    cursor = connection.cursor()
    try:
        while True:
            song_name = input("삭제할 노래 제목을 입력하세요 (종료하려면 Enter): ")
            if not song_name:
                print("노래 삭제를 종료합니다.")
                break

            query = """
                SELECT MUSIC.Music_idx 
                FROM PLAYLIST_MUSIC 
                JOIN MUSIC ON PLAYLIST_MUSIC.Music_idx = MUSIC.Music_idx 
                WHERE PLAYLIST_MUSIC.Play_idx = %s AND MUSIC.Music_name = %s
            """
            cursor.execute(query, (playlist_idx, song_name))
            music = cursor.fetchone()

            if music:
                query = "DELETE FROM PLAYLIST_MUSIC WHERE Play_idx = %s AND Music_idx = %s"
                cursor.execute(query, (playlist_idx, music[0]))
                connection.commit()
                print(f"'{song_name}' 노래가 플레이리스트에서 삭제되었습니다.")
            else:
                print(f"'{song_name}' 제목의 노래는 현재 플레이리스트에 없습니다.")

    except Exception as e:
        print(f"delete_music_from_playlist: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def delete_playlist():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("\n=== 플레이리스트 삭제 ===")

        while True:
            playlist_name = input("삭제할 플레이리스트 이름을 입력하세요: ")

            query = """
                SELECT Playlist_idx, Playlist_name 
                FROM PLAYLIST 
                WHERE Playlist_name = %s AND Owner_user_idx = %s
            """
            cursor.execute(query, (playlist_name, user_info.Uidx))
            selected_playlist = cursor.fetchone()

            if selected_playlist:
                playlist_idx = selected_playlist[0]
                break
            else:
                print(f"'{playlist_name}' 이름의 플레이리스트가 존재하지 않습니다. 다시 입력하세요.")

        query = "DELETE FROM PLAYLIST WHERE Playlist_idx = %s"
        cursor.execute(query, (playlist_idx,))
        connection.commit()

        print(f"'{playlist_name}' 플레이리스트가 삭제되었습니다.")

    except Exception as e:
        print(f"delete_playlist err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def view_all_playlists():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print("다른 사용자의 플레이리스트 보기".center(10))
        print("=" * 50)

        query = """
            SELECT Playlist_idx, Playlist_name, Uid
            FROM PLAYLIST
            JOIN USER ON Owner_user_idx = Uidx
            WHERE Owner_user_idx != %s
        """
        cursor.execute(query, (user_info.Uidx,))
        playlists = cursor.fetchall()

        if not playlists:
            print("현재 데이터베이스에 다른 사용자의 플레이리스트가 없습니다.")
            return

        print("\n플레이리스트 목록:")
        print("=" * 50)
        for idx, playlist in enumerate(playlists, start=1):
            playlist_idx, playlist_name, user_id = playlist
            print(f"{idx}. 이름: {playlist_name}, 소유자 ID: {user_id}")
        print("=" * 50)

        while True:
            try:
                choice = int(input("보고 싶은 플레이리스트 번호를 선택하세요 (돌아가기: 0): "))
                if choice == 0:
                    print("취소합니다.")
                    return
                elif 1 <= choice <= len(playlists):
                    selected_playlist = playlists[choice - 1]
                    playlist_idx = selected_playlist[0]
                    break
                else:
                    print("유효한 번호를 입력하세요.")
            except ValueError:
                print("숫자를 입력하세요.")

        print("\n선택한 플레이리스트 음악 목록:")
        print("=" * 50)
        query = """
            SELECT MUSIC.Music_name, MUSIC.Duration, MUSIC.Genre, ARTIST.Artist_name
            FROM PLAYLIST_MUSIC
            JOIN MUSIC ON PLAYLIST_MUSIC.Music_idx = MUSIC.Music_idx
            JOIN SINGERS ON MUSIC.Music_idx = SINGERS.Music_idx
            JOIN ARTIST ON SINGERS.Singer_idx = ARTIST.Artist_idx
            WHERE PLAYLIST_MUSIC.Play_idx = %s
        """
        cursor.execute(query, (playlist_idx,))
        musics = cursor.fetchall()

        if musics:
            for music in musics:
                music_name, duration, genre, artist_name = music
                print(
                    f"노래 제목: {music_name}, 재생 시간: {duration}, 장르: {genre}, 가수: {artist_name}")
            print("=" * 50)
            print("\n")

        else:
            print("이 플레이리스트에는 음악이 없습니다.")

    except Exception as e:
        print(f"view_all_playlists err: {e}")

    finally:
        cursor.close()
        connection.close()


def view_like_music():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print("좋아하는 음악 목록".center(40))
        print("=" * 50)

        query = """
            SELECT MUSIC.Music_name, MUSIC.Duration, MUSIC.Genre, GROUP_CONCAT(ARTIST.Artist_name SEPARATOR ', ') AS Artists
            FROM LIKE_MUSIC
            JOIN MUSIC ON LIKE_MUSIC.Music_idx = MUSIC.Music_idx
            JOIN SINGERS ON MUSIC.Music_idx = SINGERS.Music_idx
            JOIN ARTIST ON SINGERS.Singer_idx = ARTIST.Artist_idx
            WHERE LIKE_MUSIC.User_idx = %s
            GROUP BY MUSIC.Music_idx
        """
        cursor.execute(query, (user_info.Uidx,))
        like_music = cursor.fetchall()

        if like_music:
            print(f"\n{user_info.Uname}님 이 좋아하는 음악 목록:")
            print("=" * 50)
            for idx, music in enumerate(like_music, start=1):
                music_name, duration, genre, artists = music
                print(
                    f"{idx}. 제목: {music_name}, 재생 시간: {duration}, 장르: {genre}, 가수: {artists}")
            print("=" * 50)
            print("\n\n")
        else:
            print("좋아하는 음악이 없습니다.")

    except Exception as e:
        print(f"view_like_music err : {e}")

    finally:
        cursor.close()
        connection.close()


def search_artist():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print("가수 검색".center(40))
        print("=" * 50)

        artist_name = input("검색할 가수 이름을 입력하세요: ")
        print("\n")
        query = """
            SELECT Artist_idx, Artist_name, Info
            FROM ARTIST
            WHERE Artist_name LIKE %s
        """
        cursor.execute(query, (f"%{artist_name}%",))
        artists = cursor.fetchall()

        if artists:
            print("검색 결과".center(45))
            print("=" * 50)
            for idx, artist in enumerate(artists, start=1):
                print(
                    f"{idx}. 이름: {artist[1]}, 정보: {artist[2] if artist[2] else '정보 없음'}")
            print("=" * 50)
            while True:
                try:
                    like_artist = int(
                        input("좋아하는 가수에 추가할 가수 번호를 입력하세요 (취소: 0): "))
                    if like_artist == 0:
                        print("\n좋아하는 가수 추가를 취소했습니다.")
                        break
                    if 1 <= like_artist <= len(artists):
                        selected_artist = artists[like_artist - 1]
                        add_like_artist(selected_artist[0], selected_artist[1])
                        break
                    else:
                        print("\n유효한 번호를 입력하세요.")
                except ValueError:
                    print("\n숫자를 입력하세요.")

        else:
            print("\n검색 결과가 없습니다.")

    except pms.Error as e:
        print(f"\nsearch_artist err: {e}")

    finally:
        cursor.close()
        connection.close()


def add_like_artist(artist_idx, artist_name):

    connection = db_connect()
    cursor = connection.cursor()

    try:
        query = """
            SELECT COUNT(*) 
            FROM LIKE_ARTIST 
            WHERE User_idx = %s AND Artist_idx = %s
        """
        cursor.execute(query, (user_info.Uidx, artist_idx))
        already_like = cursor.fetchone()[0]

        if already_like:
            print(f"\n가수 '{artist_name}'은(는) 이미 좋아하는 가수 목록에 있습니다.")
            return

        query = """
            INSERT INTO LIKE_ARTIST (User_idx, Artist_idx)
            VALUES (%s, %s)
        """
        cursor.execute(query, (user_info.Uidx, artist_idx))
        connection.commit()

        print(f"\n가수 '{artist_name}'이(가) 좋아하는 가수 목록에 추가되었습니다!")

    except pms.Error as e:
        print(f"\nadd_like_artist err: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


def view_like_artist():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        print("=" * 50)
        print(f"{user_info.Uname}님 의 좋아하는 가수 목록".center(40))
        print("=" * 50)

        query = """
            SELECT ARTIST.Artist_name, ARTIST.Info
            FROM LIKE_ARTIST
            JOIN ARTIST ON LIKE_ARTIST.Artist_idx = ARTIST.Artist_idx
            WHERE LIKE_ARTIST.User_idx = %s
        """
        cursor.execute(query, (user_info.Uidx,))
        like_artists = cursor.fetchall()

        if like_artists:
            for idx, artist in enumerate(like_artists, start=1):
                print(
                    f"{idx}. 이름: {artist[0]}, 정보: {artist[1] if artist[1] else '정보 없음'}")
            print("=" * 50)
            print("\n\n")

        else:
            print("\n좋아하는 가수 목록이 비어 있습니다.")

    except pms.Error as e:
        print(f"\nview_like_artist err: {e}")

    finally:
        cursor.close()
        connection.close()


def top_streaming_musics():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        query = """
            SELECT Music_name, Duration, Genre, Likes_cnt
            FROM MUSIC
            ORDER BY Likes_cnt DESC
            LIMIT 5
        """
        cursor.execute(query)
        top_musics = cursor.fetchall()

        print("=" * 50)
        print("가장 많이 스트리밍 된 음악 Top 5".center(40))
        print("=" * 50)
        for idx, music in enumerate(top_musics, start=1):
            print(f"{idx}. 제목: {music[0]}")
            print(f"   - 재생 시간: {music[1]}")
            print(f"   - 장르: {music[2]}")
            print(f"   - 스트리밍 횟수: {music[3]}")
            print("-" * 50)
    except Exception as e:
        print(f"top_streaming_musics err: {e}")
    finally:
        cursor.close()
        connection.close()


def top_liked_musics():
    connection = db_connect()
    cursor = connection.cursor()

    try:
        query = """
            SELECT Music_name, Duration, Genre, Likes_cnt
            FROM MUSIC
            ORDER BY Likes_cnt DESC
            LIMIT 5
        """
        cursor.execute(query)
        musics = cursor.fetchall()

        if musics:
            print("=" * 50)
            print("가장 좋아요가 많은 음악 Top5 ".center(40))
            print("=" * 50)
            for idx, music in enumerate(musics, start=1):
                print(f"{idx}. 제목: {music[0]}")
                print(f"   - 재생 시간: {music[1]}")
                print(f"   - 장르: {music[2]}")
                print(f"   - 좋아요 횟수: {music[3]}")
                print("-" * 50)
        else:
            print("좋아요 데이터가 없습니다.")

    except Exception as e:
        print(f"top_liked_musics err: {e}")
    finally:
        cursor.close()
        connection.close()
