import os

from Save_Password import VaultManager
from Save_Password.VaultManager import VAULT_FOLDER


class Command:
    def __init__(self, main_password=None):
        self.vault = None
        self.completed = True
        if main_password is not None:
            self.set_main_password(main_password)

    def set_main_password(self, main_password):
        """Create the vault manager, the main password stays in memory only."""
        self.vault = VaultManager.VaultManager(VAULT_FOLDER, main_password)

    def recognition(self, command):
        """Run one command, False is returned when the program should stop."""
        command = command.strip()
        if command == "":
            return self.completed
        parts = command.split()
        action = parts[0].lower()
        args = parts[1:]

        if action == "help":
            print("""--- FastPassword 命令帮助 ---
密码条目操作：
  add <name> <remarks> <password>    新增一条密码
  add <name> <password>              新增一条没有备注的密码
  show <name>                        查看某条密码
  delete <name>                      删除某条密码
  list                               列出所有条目
  search <keyword>                    搜索条目名称

修改操作：
  update <name> <remarks> <password> 修改某条密码（会覆盖）
  update <name> <password>           修改某条密码并清空备注

主密码管理：
  passwd                             修改主密码（会提示输入旧密码和新密码）

系统命令：
  help                               显示本帮助
  clear                              清屏
  exit / quit                        退出程序
""")
        elif action == "add":
            self._cmd_add(args)
        elif action == "show":
            self._cmd_show(args)
        elif action == "delete":
            self._cmd_delete(args)
        elif action == "list":
            self._cmd_list(args)
        elif action == "search":
            self._cmd_search(args)
        elif action == "update":
            self._cmd_update(args)
        elif action == "passwd":
            self._cmd_passwd(args)
        elif action == "clear":
            self._cmd_clear(args)
        elif action == "exit" or action == "quit":
            self._cmd_exit(args)
        else:
            print(f"---Can't recognize {command} as a script, please check the spelling of the name.")
        return self.completed

    def _vault_ready(self):
        if self.vault is None:
            print("---尚未设置主密码，请重新启动并在提示时输入主密码---")
            return False
        return True

    def _load_index(self):
        """Read the index, None is returned when it cannot be decrypted."""
        try:
            return self.vault.load_index()
        except Exception:
            print("---索引解密失败，请检查主密码是否正确或数据是否已损坏---")
            return None

    def _find_entry(self, name):
        """Return (index_dict, file_id), file_id is None when not found."""
        index_dict = self._load_index()
        if index_dict is None:
            return None, None
        return index_dict, self.vault.find_index(name, index_dict)

    def _parse_entry_args(self, args, usage):
        """Parse the arguments of add/update into (name, remarks, password)."""
        if len(args) == 2:
            return args[0], "", args[1]
        if len(args) == 3:
            return args[0], args[1], args[2]
        print(usage)
        return None

    def _read_entry(self, name, file_id):
        """Decrypt one entry, None is returned when it cannot be decrypted."""
        try:
            return self.vault.load_password(file_id)
        except Exception:
            print(f"---条目 {name} 解密失败，请检查主密码是否正确或数据是否已损坏---")
            return None

    def _cmd_add(self, args):
        if not self._vault_ready():
            return
        parsed = self._parse_entry_args(args, "用法：add <name> <remarks> <password>")
        if parsed is None:
            return
        name, remarks, password = parsed
        index_dict, file_id = self._find_entry(name)
        if index_dict is None:
            return
        if file_id is not None:
            print(f"---条目 {name} 已存在，如需修改请使用 update 命令---")
            return
        index_dict = self.vault.add_index(name, index_dict)
        file_id = self.vault.find_index(name, index_dict)
        try:
            self.vault.save_password(name, remarks, password, file_id=file_id)
        except FileExistsError:
            print(f"---条目 {name} 的密码文件已存在，新增失败---")
            return
        self.vault.save_index(index_dict)
        print(f"---已新增条目 {name}---")

    def _cmd_show(self, args):
        if not self._vault_ready():
            return
        if len(args) != 1:
            print("用法：show <name>")
            return
        name = args[0]
        index_dict, file_id = self._find_entry(name)
        if index_dict is None:
            return
        if file_id is None:
            print(f"---未找到条目 {name}---")
            return
        entry = self._read_entry(name, file_id)
        if entry is None:
            return
        print(f"名称：{entry.get('name', name)}")
        print(f"备注：{entry.get('remarks') or ''}")
        print(f"密码：{entry.get('password', '')}")

    def _cmd_delete(self, args):
        if not self._vault_ready():
            return
        if len(args) != 1:
            print("用法：delete <name>")
            return
        name = args[0]
        index_dict, file_id = self._find_entry(name)
        if index_dict is None:
            return
        if file_id is None:
            print(f"---未找到条目 {name}---")
            return
        confirm = input(f"确认删除条目 {name} ？输入 YES 确认：")
        if confirm != "YES":
            print("---已取消删除---")
            return
        self.vault.delete_password(file_id)
        index_dict = self.vault.delete_index(name, index_dict)
        self.vault.save_index(index_dict)
        print(f"---已删除条目 {name}---")

    def _cmd_list(self, args):
        if not self._vault_ready():
            return
        if args:
            print("用法：list")
            return
        index_dict = self._load_index()
        if index_dict is None:
            return
        if not index_dict:
            print("---保险库中还没有任何条目---")
            return
        print(f"---共 {len(index_dict)} 条条目---")
        for number, name in enumerate(index_dict.values(), start=1):
            print(f"{number:>3}. {name}")

    def _cmd_search(self, args):
        if not self._vault_ready():
            return
        if len(args) != 1:
            print("用法：search <关键词>")
            return
        keyword = args[0].lower()
        index_dict = self._load_index()
        if index_dict is None:
            return
        matches = [name for name in index_dict.values() if keyword in name.lower()]
        if not matches:
            print(f"---没有找到与 {args[0]} 匹配的条目---")
            return
        print(f"---找到 {len(matches)} 条匹配条目---")
        for name in matches:
            print(f"    {name}")

    def _cmd_update(self, args):
        if not self._vault_ready():
            return
        parsed = self._parse_entry_args(args, "用法：update <name> <remarks> <password>")
        if parsed is None:
            return
        name, remarks, password = parsed
        index_dict, file_id = self._find_entry(name)
        if index_dict is None:
            return
        if file_id is None:
            print(f"---未找到条目 {name}，请使用 add 命令新增---")
            return
        self.vault.update_password(file_id, name, remarks, password)
        print(f"---已更新条目 {name}---")

    def _cmd_passwd(self, args):
        if not self._vault_ready():
            return
        if args:
            print("用法：passwd")
            return
        old_password = input("请输入旧主密码：")
        index_dict = self._load_index()
        if index_dict is None:
            return
        if index_dict:
            try:
                VaultManager.VaultManager(VAULT_FOLDER, old_password).load_index()
            except Exception:
                print("---旧主密码不正确，未做任何修改---")
                return
        new_password = input("请输入新主密码：")
        confirm = input("请再次输入新主密码：")
        if new_password == "":
            print("---新主密码不能为空，未做任何修改---")
            return
        if new_password != confirm:
            print("---两次输入的新主密码不一致，未做任何修改---")
            return
        entries = []
        for file_id, name in index_dict.items():
            entry = self._read_entry(name, file_id)
            if entry is None:
                print("---读取条目失败，未做任何修改---")
                return
            entries.append((file_id, entry))
        new_vault = VaultManager.VaultManager(VAULT_FOLDER, new_password)
        for file_id, entry in entries:
            new_vault.update_password(file_id, entry.get('name', ''), entry.get('remarks'), entry.get('password', ''))
        new_vault.save_index(index_dict)
        self.vault = new_vault
        print("---主密码已修改，所有条目已使用新主密码重新加密---")

    def _cmd_clear(self, args):
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    def _cmd_exit(self, args):
        self.completed = False
        print("---已退出 FastPassword---")