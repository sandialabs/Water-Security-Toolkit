
import time
from string import lower
import os

import pyutilib.services


def get_solvername(prob):
    """
    Return _the_ solver name.  This function verifies that there is a single
    solver, and it returns its name.
    """
    #if len(prob.opts['solver']) != 1:
        #msg = ''
        #for i in range(len(prob.opts['solver'])):
            #msg += prob.getSolverOption('type',i)+' '
        #raise RuntimeError, "Must have a single solver for optimizing Pyomo models.  Solvers specified: "+msg
    return lower(prob.getSolverOption('type', 0))


def createSensorsFile(results):
    #
    # Create a temporary *.sensors file
    #
    output_file = results.prefix + '.sensors'
    pyutilib.services.TempfileManager.add_tempfile(output_file, exists=False)
    #
    # Create the sensor output file, which is read by evalsensor
    #
    OUTPUT = open(output_file,"w")
    print >>OUTPUT, "#"
    print >>OUTPUT, "# Generated by sp solver interface: " + time.asctime(time.gmtime(time.time()))
    print >>OUTPUT, "#"
    print >>OUTPUT, "# " + results.command_line
    print >>OUTPUT, "# exit code " + `results.exit_code`
    print >>OUTPUT, "#"
    print >>OUTPUT, os.getpid(),
    # This next line is read by evalsensor
    if len(results.solutions) > 0:
      latestSoln = results.solutions[-1]
      latestSoln.sort()
      print >>OUTPUT, len(latestSoln)," ",
      for val in latestSoln:
        print >>OUTPUT, `val`," ",
    print >>OUTPUT, "\n#"
    # 
    # TODO: what are the response and attribute values used for?
    #
    #print >>OUTPUT, self.getLatestSolutions()
    #
    print >>OUTPUT
    OUTPUT.close()
    return output_file

def evalsensors(prob, results):
    output_file = createSensorsFile(results)
    #
    # Error checking
    #
    evalsensorExecutable = pyutilib.services.registered_executable('evalsensor')
    if evalsensorExecutable is None:
        raise RuntimeError, "The 'evalsensor' executable is not available.  Cannot summarize sensor results"
    #
    # Print summary of output
    #
    # NOTE: the 'original' impact files are used, since we are evaluating all locations
    #
    impactfiles=""
    if True or not prob.getConfigureOption('evaluate all') in prob.none_list:
        for i in range(len(prob.opts['impact data'])):
            #if prob.getImpactOption('original directory',i) not in prob.none_list:
            #    fname = os.path.join(prob.getImpactOption('original directory',i),prob.getImpactOption('original impact file',i))
            #else:
            fname = prob.getImpactOption('original impact file',i)
            if fname is None:
                #if prob.getImpactOption('directory',i) not in prob.none_list:
                #    fname = os.path.join(prob.getImpactOption('directory',i),prob.getImpactOption('impact file',i))
                #else:
                fname = prob.getImpactOption('impact file',i)
            impactfiles = impactfiles + ' ' + fname
    else:      
        # Collect impact files used objectives and constraints
        for i in range(len(prob.getProblemOption('objective'))): 
            obj_name = prob.getProblemOption('objective', prob_name)[i]
            if lower(self.getObjectiveOption('goal', obj_name)) in prob.impact_goals:
                impact_name = prob.getObjectiveOption('goal', obj_name)
                #if prob.getImpactOption('original directory',impact_name) not in prob.none_list:
                #    fname = os.path.join(prob.getImpactOption('directory',impact_name),prob.getImpactOption('impact file',impact_name))
                #else:
                fname = prob.getImpactOption('original impact file',impact_name)
                impactfiles = impactfiles + ' ' + fname
                
        for i in range(len(prob.getProblemOption('constraint'))): 
            const_name = prob.getProblemOption('constraint', prob_name)[i]
            if lower(prob.getConstraintOption('goal', const_name)) in prob.impact_goals:
                impact_name = prob.getConstraintOption('goal', const_name)
                #if prob.getImpactOption('original directory',impact_name) not in prob.none_list:
                #    fname = os.path.join(prob.getImpactOption('directory',impact_name),prob.getImpactOption('impact file',impact_name))
                #else:
                fname = prob.getImpactOption('original impact file',impact_name)
                impactfiles = impactfiles + ' ' + fname
    
    #
    # TODO: SP currenlty limited to one cost file
    #
    if prob.single_cost_file != None :
      cost_option = " --costs=" + prob.single_cost_file
    else:
      cost_option = ""
    
    #
    # TODO: SP currenlty limited to one nodemap file
    #
    if prob.single_nodemap_file != None :
      nodemap_option = " --nodemap=" + prob.single_nodemap_file
    else:
      nodemap_option = ""
    #
    # TODO: SP currently limited to one gamma value
    #
    if prob.single_gamma != None :
      gamma_option = " --gamma=" + str(prob.single_gamma)
    else:
      gamma_option = ""
      
    if prob.getProblemOption('compute greedy ranking'):
        compute_greedy_ranking=" --compute-greedy-ranking"
    else:
        compute_greedy_ranking=""
    debug = prob.getConfigureOption('debug')
    
    #cmd = evalsensorExecutable.get_path() + " --responseTime=" + `prob.delay` + " --gamma=0.05" + compute_greedy_ranking + " --format=" + prob.format_str + " --nodemap=" + prob.nodemap_file + cost_option + " " + results.output_file + " " + impactfiles
    cmd = evalsensorExecutable.get_path() + " " + gamma_option + " " + compute_greedy_ranking + " " + nodemap_option + " " + cost_option + " " + output_file + " " + impactfiles
    #
    # TODO: filter the execution of evalsensor by the problem type??
    #
    if debug:
        print cmd
    (rc, output) = pyutilib.subprocess.run(cmd)
    #
    # TODO - store output in summary file?
    #
    return output


