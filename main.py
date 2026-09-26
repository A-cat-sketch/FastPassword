import Fix_file
import getpass
from Assets.Pictures import TxT
import Command

print(TxT.HELLO)

error = Fix_file.fix_password_folder()
if error == "ERROR":
    input(">>>密码存储文件夹丢失<<<\n>>>密码可能已经丢失，已重新创建空文件夹<<<\n按任意键继续...")

error = Fix_file.fix_password_index()
if error == "ERROR":
    fix = input(">>>条目名花名册丢失<<<\n>>>密码对应名称可能已经丢失，已重新创建空花名册<<<\n如需尝试修复，请输YES\n按任意键继续...")
    if fix == "YES":
        input("功能未完善，按任意键继续...")

print("欢迎使用FastPassword，输入help查看帮助")
main_password = getpass.getpass("请输入主密码：")
while main_password == "":
    main_password = input("主密码不能为空，请重新输入主密码：")
recognition = Command.Command(main_password)
print("OK.")

while True:
    try:
        command = input(">>> ")
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if recognition.recognition(command) is False:
        break