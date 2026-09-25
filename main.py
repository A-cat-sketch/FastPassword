import Save_Password
import Fix_file
from Assets.Pictures import TxT

print(TxT.HELLO)

error = Fix_file.fix_password_folder()
if error == "ERROR":
    input(">>>密码存储文件夹丢失<<<\n>>>密码可能已经丢失，已重新创建空文件夹<<<\n按任意键继续。")