from __future__ import division
from work_queue import *

import os
import sys

port = 0
q = WorkQueue(port)
q.specify_name(project_name)
print "listening on port %d..." % q.port

# -------------------define simulation related parameters for different configurations---------------

type = "2"
project_name = "vortex_resistance_current_type" + type
data_dir = "/afs/crc.nd.edu/user/w/wli12/viscosity_data/type" + type + "/"

max_n = 200
n_step = 2
n_list = []
n = 2
while n <= max_n:
    n_list.append(n)
    n += n_step

temp_collection = []
start = 0.0
end = 10.0
step = 0.2
while start <= end:
    temp_collection.append(start)
    start += step
temp_collection = [0.0]

pdepth_list = [1.0, 2.0, 3.0]
fv_list = [1.0, 3.0, 5.0, 7.0, 9.0]
fp_list = [1.0, 3.0, 5.0]
pr_list = [1.0]

# --------------------binary search parameters---------------------

precision = 0.01

target_velocity = 40.0

min_current = 0
max_current = 50.0
mid_current = (min_current + max_current) / 2

left_current = {}
right_current = {}
task_n = {}

# --------------------submit the initial jobs with different configurations---------------------

for n in n_list:

    for temp in temp_collection:

        for pdepth in pdepth_list:

            for fv in fv_list:

                for fp in fp_list:

                    for pr in pr_list:

                        this = (n, temp, pdepth, fv, fp, pr)

                        left_current[this] = min_current
                        right_current[this] = max_current

                        command1 = "source /opt/crc/Modules/current/init/bash\n"
                        command2 = "module load python\n"
                        command3 = "python current.py {} {} {} {} {} {} {}".format(n, temp, mid_current, pdepth, fv, fp, pr)
                        t = Task(command1 + command2 +command3)

                        infile = 'data.out' + str(n) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr)

                        t.specify_file("current.py", "current.py", WORK_QUEUE_INPUT, cache=False)
                        t.specify_file(data_dir + infile, infile, WORK_QUEUE_INPUT, cache=False)
                        t.specify_file("pa.dat", "pa.dat", WORK_QUEUE_INPUT, cache=False)
                        t.specify_file("pr.dat", "pr.dat", WORK_QUEUE_INPUT, cache=False)

                        outfile = 'velocity.out_n_' + str(n) + '_temp_' + str(temp) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr)
                        t.specify_file(outfile, outfile, WORK_QUEUE_OUTPUT, cache=False)
                        taskid = q.submit(t)
                        task_n[taskid] = this
                        print "submitted task (id# %d): %s" % (taskid, t.command)


# --------------------incorporate binary search with the Work Queue APIs---------------------

while not q.empty():
    t = q.wait(1)
    if t:
        print "task (id# %d) complete: %s (return code %d)" % (t.id, t.command, t.return_status)
        if t.return_status != 0:
            print t.output
        else:
            n, temp, pdepth, fv, fp, pr = task_n[t.id]
            this = (n, temp, pdepth, fv, fp, pr)

            outfile = 'velocity.out_n_' + str(n) + '_temp_' + str(temp) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr)
            with open(outfile, 'r') as f:
                velocity = float(f.readline())
            os.system('rm {}'.format(outfile))

# -------------master performs binary search based on the output from the workers--------------

            mid = (right_current[this] + left_current[this]) / 2
            if velocity > target_velocity:
                right_current[this] = mid
            else:
                left_current[this] = mid

            if right_current[this] - left_current[this] < precision:
                with open('current.out_n_' + str(n) + '_temp_' + str(temp)+ '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr), 'w') as f:
                    f.write('{}\n'.format(right_current[this]))
            else:
                mid = (right_current[this] + left_current[this]) / 2
                command1 = "source /opt/crc/Modules/current/init/bash\n"
                command2 = "module load python\n"
                command3 = "python current.py {} {} {} {} {} {} {}".format(n, temp, mid, pdepth, fv, fp, pr)

                t = Task(command1 + command2 +command3)
                t.specify_file("current.py", "current.py", WORK_QUEUE_INPUT, cache=False)

                infile = 'data.out' + str(n) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr)

                t.specify_file(data_dir + infile, infile, WORK_QUEUE_INPUT, cache=False)
                t.specify_file("pr.dat", "pr.dat", WORK_QUEUE_INPUT, cache=False)
                t.specify_file("pa.dat", "pa.dat", WORK_QUEUE_INPUT, cache=False)

                outfile = 'velocity.out_n_' + str(n) + '_temp_' + str(temp) + '_pdepth' + str(pdepth) + '_fv' + str(fv) + '_fp' + str(fp) + '_pr' + str(pr)
                t.specify_file(outfile, outfile, WORK_QUEUE_OUTPUT, cache=False)
                taskid = q.submit(t)
                task_n[taskid] = this
                print "submitted task (id# %d): %s" % (taskid, t.command)
