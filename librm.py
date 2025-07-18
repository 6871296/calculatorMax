#用于自动删除easygui等在程序中调用过的库。请在相同版本的Python中运行！
import subprocess,sys
max=3 #最多尝试几次，可自由调整
for i in range(1,max)
  subprocess.run([sys.execytable,"-m","pip","uninstall","easygui"])
  try:
    import easygui
  except ImportError:
    print("Sucsessfully removed 1 library. main.py'll automatically install them when you use it.")
    sys.exit()
  print("Removation failed when trying "+i+'/'+max+" times.")
print("Removation failed!")
