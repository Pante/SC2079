from config import get_config
from task1_pc import main as t1_main
from task2_pc import main as t2_main

task_dict = {
    1: t1_main,
    2: t2_main
}

task_num = None
while task_num is None:
    task_num_str = input("Enter task number (1 / 2) >> ")
    try:
        task_num = int(task_num_str)
        if task_num not in [1, 2]:
            print("Please enter either 1 or 2.")
            task_num = None
            continue
    except:
        print("Please enter a valid number.")

config = get_config()
task_dict[task_num](config)