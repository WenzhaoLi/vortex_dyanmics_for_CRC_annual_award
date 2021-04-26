
from work_queue import *

import os
import sys

# -------------------------- Define simulation parameters -------------------------

project_name = "vortex_annealing"

max_n = 100

each_steps = 2500

iteration = 2

temp_list = []
temperature = 40
while temperature >= 20:
    temp_list.append(temperature)
    temperature -= 2
temperature = 10
while temperature >= 0:
    temp_list.append(temperature)
    temperature -= 1

pdepth_list = [0.6, 0.8, 1.0, 1.3]
fv_list = [0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
fp_list = [0.8]
pr_list = [1.0]


task_n = {}
count_n = {}
temp_n = {}

if __name__ == '__main__':

    port = 0

# -------------------------- Create a Work Queue instance --------------------------
    q = WorkQueue(port)
    q.specify_name(project_name)
    q.blacklist("d8civy138.crc.nd.edu")
    print "listening on port %d..." % q.port
    
# -------------------------- Submit initial jobs --------------------------
 
    for pdepth in pdepth_list:
        for fv in fv_list:
            for fp in fp_list:
                for pr in pr_list:
                    for i in range(1, max_n+1):

                        n = i * 2

                        this = (n, pdepth, fv, fp, pr)
                        count_n[this] = 0
                        temp_n[this] = 0

                        command1 = "source /opt/crc/Modules/current/init/bash\n"
                        command2 = "module load python\n"
                        command3 = "python anneal.py {} {} {} {} {} {} {}".format(n, temp_list[0], each_steps, pdepth, fv, fp, pr)
                        t = Task(command1 + command2 +command3)
                        t.specify_file("anneal.py", "anneal.py", WORK_QUEUE_INPUT, cache=False)
                        t.specify_file("pa.dat", "pa.dat", WORK_QUEUE_INPUT, cache=False)
                        t.specify_file("pr.dat", "pr.dat", WORK_QUEUE_INPUT, cache=False)
                        outfile = 'data.out.new' + str(n) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr) 
                        t.specify_file(outfile, outfile, WORK_QUEUE_OUTPUT, cache=False)
                        taskid = q.submit(t)
        
                        task_n[taskid] = this
                
                        print("submitted task (id# %d): %s" % (taskid, t.command))

    print("waiting for tasks to complete...")

    
# -------------------------- Continue to submit jobs if the temperature is greater than zero --------------------------

    while not q.empty():
        t = q.wait(1)
        if t:
            print "task (id# %d) complete: %s (return code %d)" % (t.id, t.command, t.return_status)
            if t.return_status != 0:
                print t.output
            else:
                this = task_n[t.id]
                n, pdepth, fv, fp, pr = this

                old_file = "data.out" + str(n) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr) 
                new_file = 'data.out.new' + str(n) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr) 

                if os.path.exists(old_file):
                    os.system("rm {}".format(old_file))
                os.system("mv {} {}".format(new_file, old_file))

                count_n[this] += 1
                if count_n[this] == iteration:
                    count_n[this] = 0
                    temp_n[this] += 1

                if temp_n[this] < len(temp_list):

                    temp = temp_list[temp_n[this]]
                    command1 = "source /opt/crc/Modules/current/init/bash\n"
                    command2 = "module load python\n"
                    command3 = "python anneal.py {} {} {} {} {} {} {}".format(n, temp, each_steps, pdepth, fv, fp, pr)
                    t = Task(command1 + command2 +command3)
                    t.specify_file("anneal.py", "anneal.py", WORK_QUEUE_INPUT, cache=False)
                    t.specify_file("pa.dat", "pa.dat", WORK_QUEUE_INPUT, cache=False)
                    t.specify_file("pr.dat", "pr.dat", WORK_QUEUE_INPUT, cache=False)
                    t.specify_file(old_file, old_file, WORK_QUEUE_INPUT, cache=False)
                    t.specify_file(new_file, new_file, WORK_QUEUE_OUTPUT, cache=False)
                    taskid = q.submit(t)
                    task_n[taskid] = this

                    print "submitted task (id# %d): %s" % (taskid, t.command)

    sys.exit(0)
