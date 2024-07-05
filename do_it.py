import elevate
import sys
import winreg

MODE_DISABLE = "disable"
MODE_ENABLE = "enable"
MODE_ILLEGAL = "ILLEGAL"
ALL_MODES = (MODE_DISABLE, MODE_ENABLE)
USAGE_TIP = f'''
Usage: do_it.py -m [|mode|]
[|mode|]: {MODE_DISABLE}/{MODE_ENABLE}

You can restart this program with correct params or type in the mode below manually;
Type in \"exit\" to exit.
'''
A_DOUBT = Exception("Why would this happen?")

mode = None

def evaluate_mode(new_mode=None):
	# Returns if the mode is legal.
	global mode
	if new_mode is not None:
		mode = new_mode
	if mode not in ALL_MODES:
		mode = MODE_ILLEGAL
		return 0
	return 1

def evaluate_param():
	global mode
	if len(sys.argv) < 3 or sys.argv[1] != "-m" or not evaluate_mode(sys.argv[2]):
		while True:
			print(USAGE_TIP)
			mode = input("mode: ")
			if mode == "exit":
				return -1
			elif evaluate_mode():
				return 0
	return 0
	

def main():
	global mode
	elevate.elevate(graphical=False)
	
	if (ret := evaluate_param()) < 0:
		return ret
	#print(mode)
	
	ret = 0
	value_name = "ImagePath"
	ori_suffix = ".exe"
	new_suffix = ".exeSkyacinonaepBaned"
	for sub_key in (
		r"SYSTEM\CurrentControlSet\Services\UsoSvc",
		r"SYSTEM\CurrentControlSet\Services\WaaSMedicSvc",
		r"SYSTEM\CurrentControlSet\Services\wuauserv"
	):
		# Read
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key, 0, winreg.KEY_READ)
		value = winreg.QueryValueEx(key, value_name)[0]
		winreg.CloseKey(key)
		
		# Modify
		if mode == MODE_DISABLE:
			if value.find(new_suffix) != -1:
				ret += 1
			else:
				value = value.replace(ori_suffix, new_suffix)
		elif mode == MODE_ENABLE:
			while value.find(new_suffix) != -1:
				value = value.replace(new_suffix, ori_suffix)
		else:
			raise A_DOUBT
		
		# Write
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key, 0, winreg.KEY_WRITE)
		winreg.SetValueEx(key, value_name, 0, winreg.REG_EXPAND_SZ, value)
		winreg.CloseKey(key)
	return ret

if __name__ == "__main__":
	ret = main()
	if ret == -1:
		print("Modification failed.")
	elif ret == 0:
		print("Modification succeeded.")
	elif ret >= 1:
		print(f"Modification was canceled for {ret} times: WinUpdate was already {mode}d.")
	else:
		raise A_DOUBT
	input("Press Enter to exit.")
	exit(ret)


