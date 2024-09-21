import csv
import struct
import sys
from math import ceil


class Node:
    def __init__(self, is_leaf, b, position=None):
        self.is_leaf = is_leaf  # leaf node flag
        self.b = b  # 최대 자식 개수 (최대 키 개수 : b-1)
        self.m = 0  # 현재 키 개수
        self.key = [-1] * (b-1)
        self.leftchild = [-1] * (b-1)  # -1: none
        self.rightchild = -1  # 노드의 가장 오른쪽 자식 포인터 (leaf : sibling )
        self.position = position  # 노드의 바이너리 파일 내 위치 (오프셋으로 사용)

    def to_bytes(self):
        # is_leaf : bool (?), b: int (i), m:int, keys: (int*(b-1)), leftchild: (int(b-1)), rightchild:int, position: int
        format_str = f'<?ii{self.b-1}i{self.b-1}iii'

        # pack: 바이너리로 변환해줌
        return struct.pack(format_str, self.is_leaf, self.b, self.m,
                           *self.key, *self.leftchild, self.rightchild, self.position)

    def from_bytes(self, data):
        # 바이너리 데이터를 파이썬 객체로 변환
        format_str = f'<?ii{self.b - 1}i{self.b - 1}iii'
        unpacked_data = struct.unpack(format_str, data)

        # unpack된 데이터를 클래스의 속성으로 할당
        # unpack 은 항상 tuple 형태로 반환함 -> 값을 쓰려면 [0] 등으로 할당해야함
        self.is_leaf = unpacked_data[0]
        self.b = unpacked_data[1]
        self.m = unpacked_data[2]
        self.key = list(unpacked_data[3:3 + (self.b-1)])
        self.leftchild = list(
            unpacked_data[3 + (self.b - 1):3 + 2 * (self.b-1)])
        self.rightchild = unpacked_data[3 + 2 * (self.b-1)]  # int 값
        self.position = unpacked_data[3 + 2 *
                                      (self.b - 1) + 1]  # 그 다음 ㅑint 값

    def add_key(self, tree, key, value, is_split=False):
        # 노드가 가득 찼고 분할을 아직 하지 않은 경우
        if not is_split and (self.m >= self.b - 1):
            return self.split(tree, key, value)

        # 키를 삽입할 위치 찾기
        insert_idx = 0
        while insert_idx < self.m and self.key[insert_idx] < key:
            insert_idx += 1
        # 중복된 키가 있는지 확인
        if insert_idx < self.m and self.key[insert_idx] == key:
            print("중복된 키 삽입", key)
            return
        # 오른쪽으로 키를 이동하여 공간을 확보
        for i in range(self.m, insert_idx, -1):
            self.key[i] = self.key[i - 1]
            self.leftchild[i] = self.leftchild[i - 1]
        # 새로운 키와 값을 삽입
        self.key[insert_idx] = key
        self.leftchild[insert_idx] = value
        self.m += 1  # 현재 키의 개수를 업데이트
        # 분할이 아닌 경우에만 업데이트
        if not is_split:
            tree.update_node(self)  # 현재 노드가 변경됨

    def split(self, tree, key, value):

        # split 하기 전에 임의로 배열 크기 증가시켜놓음 (고정 크기 +1) -> 노드 업데이트 할 때는 줄여져야함 (확인)
        self.key.append(-1)
        self.leftchild.append(-1)

        self.add_key(tree, key, value, is_split=True)

        mid_idx = (self.b)//2
        mid_key = self.key[mid_idx]

        # 추가
        mid_key_leftchild = self.leftchild[mid_idx]
        print("mid key", mid_key)

        # 리프 노드인 경우
        if self.is_leaf:
            # left child node 만들기
            # original node 의 처음 ~ mid 전까지 삽입
            new_node = tree.create_node(is_leaf=True)

            # 왼쪽 자식 노드의 키
            left_key = [-1] * (self.b-1)
            left_leftchild = [-1] * (self.b-1)
            for i in range(mid_idx):
                left_key[i] = self.key[i]
                left_leftchild[i] = self.leftchild[i]

            right_key = [-1] * (self.b-1)
            right_leftchild = [-1] * (self.b-1)
            for i in range(mid_idx, len(self.key)):
                right_key[i-mid_idx] = self.key[i]
                right_leftchild[i-mid_idx] = self.leftchild[i]

            # original node 가 오른쪽 자식 노드가 됨
            self.key = right_key
            self.leftchild = right_leftchild
            self.m = len([key for key in right_key if key != -1])

            # 새로운 노드 == 왼쪽 자식 노드
            new_node.key = left_key
            new_node.leftchild = left_leftchild
            new_node.m = len([key for key in left_key if key != -1])
            # 왼쪽 자식 노드(leaf)의 rightchild는 오른쪽 자식 노드(leaf)(self) 를 가리킴
            new_node.rightchild = self.position

            # 왼쪽 자식 노드와 오른쪽 자식 노드 (지금은 현재 노드) 가 변경됨 -> 업데이트
            tree.update_node(new_node)
            tree.update_node(self)
            # print("\n\n왼쪽 자식 노드\n", new_node)
            # print("\n\n 오른쪽 자식 노드\n", self)

            # range search
            # 분할 후 midkey 값과 midleftchild(새로만든 왼쪽 자식 노드) 값을 부모 노드로 올려줘야함
            parent_node = self.load_parent_node(tree, self)
            # print("\nparent node is\n", parent_node)
            # 부모노드가 있다면 (루트 노드가 아닌 경우)
            if parent_node:
                # # original 노드를 right child 로 가리키던 leaf 가 있다면, new node 로 연결해줘야함
                left_sibling = self.find_leftsibling(tree, self)
                if left_sibling:
                    print("left sibling\n", left_sibling)
                    left_sibling.rightchild = new_node.position
                    tree.update_node(left_sibling)

                parent_node.add_key(tree, mid_key, new_node.position)
                tree.update_node(parent_node)  # parent 노드 변경됨 -> 업데이트

                return  # return 값 필요?

            else:  # 현재가 루트 노드인 경우
                new_root = tree.create_node(is_leaf=False)  # 새로운 루트 노드 만들고
                tree.update_root_position(new_root.position)

                new_root.add_key(tree, mid_key, new_node.position)  # 키 값 추가후

                new_root.rightchild = self.position  # 오른쪽 자식 노드를 현재 노드로 설정
                tree.update_node(new_root)

        # 인터널 노드인 경우
        else:
            # left child node 만들기
            # original node 의 처음 ~ mid 전까지 삽입
            new_node = tree.create_node(is_leaf=False)

            # 왼쪽 자식 노드의 키
            left_key = [-1] * (self.b-1)
            left_leftchild = [-1] * (self.b-1)
            for i in range(mid_idx):
                left_key[i] = self.key[i]
                left_leftchild[i] = self.leftchild[i]

            right_key = [-1] * (self.b-1)
            right_leftchild = [-1] * (self.b-1)
            for i in range(mid_idx+1, len(self.key)):
                right_key[i-mid_idx-1] = self.key[i]
                right_leftchild[i-mid_idx-1] = self.leftchild[i]

            # original node 가 오른쪽 자식 노드가 됨
            self.key = right_key
            self.leftchild = right_leftchild
            self.m = len([key for key in right_key if key != -1])

            # 새로운 노드 == 왼쪽 자식 노드
            new_node.key = left_key
            new_node.leftchild = left_leftchild
            new_node.m = len([key for key in left_key if key != -1])
            # 왼쪽 자식 노드(leaf)의 rightchild는 mid_key 의 왼쪽 자식 노드를 가리킴
            new_node.rightchild = mid_key_leftchild

            tree.update_node(new_node)
            tree.update_node(self)

            mid_key_leftchild = new_node.position
            # 분할 후 midkey 값과 midleftchild(새로만든 왼쪽 자식 노드) 값을 부모 노드로 올려줘야함
            parent_node = self.load_parent_node(tree, self)

            # 부모노드가 있다면 (루트 노드가 아닌 경우)
            if parent_node:
                parent_node.add_key(tree, mid_key, mid_key_leftchild)
                tree.update_node(parent_node)  # parent 노드 변경됨 -> 업데이트

                return  # return 값 필요?

            else:  # 현재가 루트 노드인 경우
                new_root = tree.create_node(is_leaf=False)  # 새로운 루트 노드 만들고
                tree.update_root_position(new_root.position)

                new_root.add_key(tree, mid_key, mid_key_leftchild)  # 키 값 추가후

                new_root.rightchild = self.position  # 오른쪽 자식 노드를 현재 노드로 설정
                tree.update_node(new_root)

    def delete_key(self, tree, key):
        # 노드에서 지울 키 값 찾고, key, value 지우기 (-1)
        for idx, node_key in enumerate(self.key):
            if node_key == key:
                self.key[idx] = -1
                self.leftchild[idx] = -1
                self.m -= 1
                break
        # 노드에서 키 값 빼고 노드 정리
        self.sort_node(idx)
        tree.update_node(self)

        # 노드 정렬

    def sort_node(self, idx):
        # 노드 당기기 (현재 지운 idx 뒤에 값이 남아있으면)
        max_idx = self.b-2  # 최대 키 개수: b-1, idx 는 0부터 시작
        if (idx) < (max_idx):
            for i in range(idx, max_idx):
                # if self.key[i] == -1:
                #     break
                self.key[i] = self.key[i+1]
                self.leftchild[i] = self.leftchild[i+1]
            self.key[max_idx] = -1
            self.leftchild[max_idx] = -1

    def find_min_key(self, tree, node):
        while not node.is_leaf:
            node = tree.load_node(node.leftchild[0])
        # 리프의 가장 작은 값 리턴
        return node.key[0]

    def find_sibling(self, tree, parent_node):
        cur_node = self
        max_idx = self.b-2
        find_flag = False
        # print("cur node is\n",cur_node)
        # print("parent_node is \n",parent_node)
        for idx, leftchild in enumerate(parent_node.leftchild):
            if cur_node.position == leftchild:
                find_flag = True
                break
        if (find_flag):
            # print("idx is",idx,"\n")
            # 현재 노드가 부모의 가장 왼쪽 자식이었을 경우, l_s 없음
            if idx == 0:
                left_sibling = None
            else:  # 아니라면 l_s는 부모노드의 한칸 전 leftchild
                left_sibling = tree.load_node(parent_node.leftchild[idx-1])
            # 현재 노드가 부모의 가장 끝쪽 키의 왼쪽 자식이었으면,
            if idx == max_idx or idx == parent_node.m-1:  # 이 조건이 중복인가?
                right_sibling = tree.load_node(parent_node.rightchild)
            else:
                right_sibling = tree.load_node(parent_node.leftchild[idx+1])
        # 현재 노드가 부모의 가장 오른쪽 자식이었을 경우
        else:
            idx = parent_node.m-1  # 현재 들어있는 부모 키의 가장 오른쪽 (idx : 0)
            left_sibling = tree.load_node(parent_node.leftchild[idx])
            right_sibling = None
        return left_sibling, right_sibling

    # split 에서는 leftsibling 만 필요 => load 수 줄이기 위해 함수 나눠 짬
    def find_leftsibling(self, tree, cur_node):
        node = tree.load_root_node()
        while not node.is_leaf:
            node_position = node.leftchild[0]
            print("\nnode posi is", node_position)
            node = tree.load_node(node_position)
        while node:
            if node.rightchild == cur_node.position:
                return node
                break
            elif node.rightchild != -1:
                node = tree.load_node(node.rightchild)
            else:
                node = None

    def borrow_left_sibling(self, tree, left_sibling, parent_node, key):
        for idx, leftchild in enumerate(parent_node.leftchild):
            if left_sibling.position == leftchild:
                break
        # left sibling 의 가장 오른쪽 키
        rightmost = left_sibling.m-1
        tmp_key = left_sibling.key[rightmost]
        tmp_value = left_sibling.leftchild[rightmost]
        left_sibling.delete_key(tree, tmp_key)
        parent_node.key[idx] = tmp_key
        tree.update_node(parent_node)
        self.delete_key(tree, key)
        self.add_key(tree, tmp_key, tmp_value)

    def borrow_right_sibling(self, tree, right_sibling, parent_node, key):
        find_flag = False
        for idx, leftchild in enumerate(parent_node.leftchild):
            if right_sibling.position == leftchild:
                find_flag = True
                idx -= 1
                break

        if not find_flag:
            idx = parent_node.m-1
        tmp_key = right_sibling.key[0]
        tmp_value = right_sibling.leftchild[0]
        right_sibling.delete_key(tree, tmp_key)
        self.delete_key(tree, key)
        self.add_key(tree, tmp_key, tmp_value)
        parent_node.key[idx] = right_sibling.key[0]
        tree.update_node(parent_node)

    def load_parent_node(self, tree, target_node):
        root_node = tree.load_root_node()

        # 부모가 없음 -> 현재 노드가 루트 노드인 경우
        if root_node.position == target_node.position:
            return None

        cur_node = root_node
        parent_node = None

        while not cur_node.is_leaf:
            find_flag = False

            for key, leftchild in zip(cur_node.key, cur_node.leftchild):
                # 부모 노드 찾은 경우
                if leftchild != -1 and leftchild == target_node.position:
                    parent_node = cur_node
                    return parent_node

                # 타겟 노드의 첫번째 키 값이 현재 노드의 키 값보다 작으면 현재 노드의 leftchild 로 이동
                if key != -1 and key > target_node.key[0]:
                    leftchild_position = leftchild
                    cur_node = tree.load_node(leftchild_position)
                    find_flag = True
                    break
            # for 문 돌았는데 없었다면 (현재 노드에 있는 키들보다 큰 키를 찾는 것) -> rightmost child 로 이동
            if not find_flag and cur_node.rightchild != -1:
                rightchild_position = cur_node.rightchild
                if target_node.position == rightchild_position:
                    parent_node = cur_node
                    return parent_node
                else:
                    cur_node = tree.load_node(rightchild_position)

        return None

    def __str__(self):
        # 노드의 속성 프린트  (디버깅용)
        return (f"Node(position={self.position}, is_leaf={self.is_leaf}, "
                f"m={self.m}, keys={self.key}, leftchild={self.leftchild}, "
                f"rightchild={self.rightchild})")

    @staticmethod
    def get_node_size(b):
        # 고정된 노드의 크기 계산 -> 매번 이 크기로 할당해줘야함
        return struct.calcsize(f'<?ii{b - 1}i{b - 1}iii')


class BPTree:
    def __init__(self, index_file, b=None):
        self.index_file = index_file
        self.b = b

        if b is not None:  # create
            self.node_size = Node.get_node_size(b)  # 고정된 노드 크기
        else:  # create 가 아니면, 기존 인덱스 파일을 사용해야함
            self.load_index_file()

    def load_index_file(self):
        with open(self.index_file, 'rb') as file:
            header_b = file.read(4)
            self.b = struct.unpack('i', header_b)[0]
            self.node_size = Node.get_node_size(self.b)

    # 노드를 만들고 파일에 쓴 뒤 , 해당 노드를 반환함
    def create_node(self, is_leaf):
        with open(self.index_file, 'ab+') as file:
            # 파일의 현재 위치 -> 오프셋
            position = file.tell()
            node = Node(is_leaf, self.b, position)
            file.write(node.to_bytes())
            return node

    # 노드 불러오기
    def load_node(self, position):
        with open(self.index_file, 'rb') as file:
            file.seek(position)
            node_data = file.read(self.node_size)

        node = Node(is_leaf=False, b=self.b)  # 임시 노드 객체 (leaf 변동되는지 확인할 것)
        node.from_bytes(node_data)
        return node

    # 노드에 변경사항이 파일에 생기면 업데이트
    def update_node(self, node):
        with open(self.index_file, 'r+b') as file:
            file.seek(node.position)
            file.write(node.to_bytes())

    # 루트 노드 위치가 바뀌면 업데이트
    def update_root_position(self, root_node_position):
        with open(self.index_file, 'r+b') as file:
            # b 다음에 root node position 저장됨 , 4까지 b, 8 까지 node posi
            file.seek(4)
            file.write(struct.pack('i', root_node_position))

    # 루트 노드 불러오기
    def load_root_node(self):
        # 헤더를 읽어와서 root node 위치를 얻어냄
        with open(self.index_file, 'rb') as file:
            file.seek(4)
            root_node_position = struct.unpack('i', file.read(4))[0]

            if root_node_position == -1:

                return None

            return self.load_node(root_node_position)

    def create_index_file(self):
        with open(self.index_file, 'wb') as file:
            # file.seek(0) 파일을 wb 모드로 열면 파일 포인터가 0번 위치로 자동 설정
            # header 작성 , header = b, root node position
            header = struct.pack('ii', self.b, -1)  # 최초 루트 노드 위치는 -1 로 임의 설정
            file.write(header)

    def search(self, key, node):
        if not node.is_leaf:
            print(','.join(str(k) for k in node.key if k != -1))

        with open(self.index_file, 'rb') as file:
            if node.is_leaf:
                # leaf node 의 키 값을 순회함 (해당 키 값의 leftchild (이 경우에는 value) 를 반환하기 위해 idx 같이 돌기)
                for idx, node_key in enumerate(node.key):
                    if node_key == key:
                        # leaf node 의 leftchild == value
                        print(node.leftchild[idx])
                        # return node.leftchild[idx]
                        return node  # 딜리트 위해 찾은 리프 노드 반환
                print("search - not found")
                return node  # 키 값이 존재하지 않음 -> insert 위해 leaf node 반환
            else:
                for idx, node_key in enumerate(node.key):
                    # 작으면 왼쪽 자식 노드로 이동
                    if node_key != -1 and key < node_key:
                        leftchild_position = node.leftchild[idx]  # 왼쪽 자식 오프셋
                        if leftchild_position != -1:
                            leftchild_node = self.load_node(leftchild_position)
                            return self.search(key, leftchild_node)
                        else:
                            # print("search: leftchild error")
                            return None
                    # 크거나 같으면 오른쪽 자식 노드로 이동해야함 (오른쪽 키의 왼쪽 child)
                    elif node_key != -1 and key >= node_key:
                        continue
                # 모든 키 순회한 후에도 없으면 노드의 가장 오른쪽 자식 노드로 이동해야함
                rightchild_position = node.rightchild
                if rightchild_position != -1:
                    rightchild_node = self.load_node(rightchild_position)
                    return self.search(key, rightchild_node)
                else:
                    # print("search: rightchild node error")
                    return None

    def range_search(self, node):
        with open(self.index_file, 'rb') as file:
            print("node posi is", node.position)
            while not node.is_leaf:
                node_posi = node.leftchild[0]
                print("\nnode posi is", node_posi)
                node = tree.load_node(node_posi)

            while node:
                for idx, key in enumerate(node.key):
                    if key != -1:
                        print("key , value", key, node.leftchild[idx])
                # 다음 리프 노드로 이동
                if node.rightchild != -1:
                    node = tree.load_node(node.rightchild)
                else:
                    node = None

    def insert(self, key, value):
        key = int(key)
        value = int(value)

        root_node = tree.load_root_node()
        if root_node is None:
            root_node = tree.create_node(is_leaf=True)
            tree.update_root_position(root_node.position)

        insert_node = self.search(key, root_node)
        print("\n\ninsert key is ", key, "insert node is\n", insert_node)

        insert_node.add_key(self, key, value)

    # 진행 상황:
    # 1. 최소 키 만족할 경우 (index 있을때 없을 때 )-> 인덱스 삭제해줌
    # 2.  최소키 만족하지 않는 경우
    # left sibling 여유 키 있을 때 빌려오기
    
    def delete(self, key):
        key = int(key)
        min_key_num = int(ceil(self.b/2)-1)
        print("minkeynum", min_key_num)

        root_node = self.load_root_node()
        delete_node = self.search(key, root_node)  # search 에서 찾은 리프 노드 받기
        max_idx = self.b-2  # 최대 자식 갯수 : b-1, idx 0부터~

        #  # case 01 : 부모 노드의 첫번째 키의 왼쪽 leftchild 노드
        #  # == 부모 노드의 첫번째 키보다 작으면
        # if parent_node.key[0] > key:
        #     delete_node.delete_key(self, key)
        parent_node = delete_node.load_parent_node(self, delete_node)

        if delete_node.m is not min_key_num:
            delete_node.delete_key(self, key)

        else:  # 현재 키가 최소 키 -> 삭제 후 재조정 필요 && 형제 노드에 여유 키가 있는 경우
            left_sibling, right_sibling = delete_node.find_sibling(
                self, parent_node)
            print("left_sibling is\n", left_sibling)
            print("\n right_sibling is \n", right_sibling)
            if (left_sibling and left_sibling.m != min_key_num):
                delete_node.borrow_left_sibling(
                    self, left_sibling, parent_node, key)
            elif (right_sibling and right_sibling.m != min_key_num):
                delete_node.borrow_right_sibling(
                    self, right_sibling, parent_node, key)
        # 인터널 노드 내부에 인덱스가 존재한다면 변경해주어야함 -> 해당 노드의 오른쪽 자식 노드를 타고가서 가장 작은값 가져오기

        while parent_node is not None:
            for idx, node_key in enumerate(parent_node.key):
                if node_key == key:
                    if (idx == max_idx or parent_node.leftchild[idx+1] == -1):
                        right_child = self.load_node(parent_node.rightchild)
                        min_key = parent_node.find_min_key(self, right_child)
                    else:
                        right_child = self.load_node(
                            parent_node.leftchild[idx+1])
                        min_key = right_child.find_min_key(self, right_child)
                    parent_node.key[idx] = min_key
                    self.update_node(parent_node)
            parent_node = parent_node.load_parent_node(self, parent_node)

    # 디버깅용

    def print_node(self, position):
        node = self.load_node(position)
        print(node)

    # 디버깅용 헤더 프린트
    def print_header(self):
        # 헤더를 읽어와서 b와 root node의 위치를 출력
        with open(self.index_file, 'rb') as file:
            # 헤더에서 b와 root node position 읽기
            # 헤더의 총 크기는 8바이트: 'ii' (b와 root_position)
            header_data = file.read(8)
            b, root_node_position = struct.unpack('ii', header_data)
            print(
                f"Header -> b: {b}, Root Node Position: {root_node_position}")

    # 디버깅용 모든 노드 프린트
    def traverse_and_collect(self, node=None, nodes=None):
        if nodes is None:
            nodes = []
        if node is None:
            node = self.load_root_node()
            if node is None:
                print("No root node found.")
                return nodes

        nodes.append(node)
        if not node.is_leaf:
            for leftchild in node.leftchild:
                if leftchild != -1:
                    child_node = self.load_node(leftchild)
                    self.traverse_and_collect(child_node, nodes)
            if node.rightchild != -1:
                rightchild_node = self.load_node(node.rightchild)
                self.traverse_and_collect(rightchild_node, nodes)
        return nodes


if __name__ == "__main__":
    cmd = sys.argv[1]
    index_file = sys.argv[2]

    if cmd == '-c':
        b = int(sys.argv[3])

        tree = BPTree(index_file, b)
        tree.create_index_file()

    if cmd == '-i':
        input_file = sys.argv[3]

        tree = BPTree(index_file)

        with open(input_file, 'r') as file:
            input_data = csv.reader(file)

            for input in input_data:
                root_node = tree.load_root_node()
                tree.insert(input[0], input[1])

    if cmd == '-s':
        key = int(sys.argv[3])

        tree = BPTree(index_file)
        # root node 생성
        root_node = tree.load_root_node()
        # tree.update_root_position(root_node.position)

        tree.search(key, root_node)

    if cmd == '-d':
        delete_file = sys.argv[3]
        tree = BPTree(index_file)

        with open(delete_file, 'r') as file:
            delete_date = csv.reader(file)

            for delete in delete_date:
                root_node = tree.load_root_node()
                tree.delete(delete[0])

    # 디버깅용 - 헤더 프린트
    if cmd == '-ph':
        tree = BPTree(index_file)
        all_nodes = tree.traverse_and_collect()
        for node in all_nodes:
            print(node)
        tree.print_header()

    if cmd == '-r':
        tree = BPTree(index_file)
        root_node = tree.load_root_node()

        tree.range_search(root_node)
