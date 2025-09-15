#用于自动删除easygui等在程序中调用过的库。请在相同IDLE中运行！
import subprocess,sys
max=3#最多尝试几次，可自由调整
libs={"easygui":False,"simpleeval":False}#所有库是否已卸载成功
print("uninstalling libs:")
for i in libs:
    print(i)
print()
for i in range(1,max):
    for l in libs:
        if libs[l]:
            subprocess.run([sys.executable,"-m","pip","uninstall",l])
            try:
                eval("import "+l)
                print("Failed to uninstall "+l)
            except ImportError:
                print("Sucsessfully uninstalled "+l)
                libs[i]=True
    if False not in libs.values():
        print("\nSucsessfully uninstalled "+len(libs)+" libraries.")
        sys.exit()
print("Removation failed!")