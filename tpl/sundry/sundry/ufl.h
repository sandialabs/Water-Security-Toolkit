/*  _________________________________________________________________________
 *
 *  Acro: A Common Repository for Optimizers
 *  Copyright (c) 2008 Sandia Corporation.
 *  This software is distributed under the CPL License.
 *  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
 *  the U.S. Government retains certain rights in this software.
 *  For more information, see the README.txt file in the top Acro directory.
 *  _________________________________________________________________________
 */

// Copyright (C) 2000, International Business Machines
// Corporation and others.  All Rights Reserved.

#ifndef __UFL_HPP__
#define __UFL_HPP__

#include <cstdio>
#include <cfloat>
#include <string>
#include <vector>
#include <cstring>
//#include <map>
#include <sundry/SMVkernel.h>

#include <sundry/VolVolume.h>

using namespace std;

// parameters controlled by the user
class UFL_parms {
public:
  std::string fdata; // file with the data
  std::string dualfile; // file with an initial dual solution
  std::string dual_savefile; // file to save final dual solution
  std::string int_savefile; // file to save primal integer solution
  int h_iter; // number of times that the primal heuristic will be run
  // after termination of the volume algorithm
   
  UFL_parms(): fdata(""), dualfile(""), dual_savefile(""), int_savefile("sensors.txt"), h_iter(100){}

  UFL_parms(const char* filename);
  ~UFL_parms() {}
};



class UFL : public VOL_user_hooks {
public:
  // for all hooks: return value of -1 means that volume should quit
  // compute reduced costs
   int compute_rc(const VOL_dvector& u, VOL_dvector& rc);
  // solve relaxed problem
   int solve_subproblem(const VOL_dvector& u, const VOL_dvector& rc,
			double& lcost, VOL_dvector& x, VOL_dvector&v,
			double& pcost);
  // primal heuristic
  // return DBL_MAX in heur_val if feas sol wasn't/was found 
   int heuristics(const VOL_problem& p, 
		  const VOL_dvector& x, double& heur_val, double lb);
   int heuristics_aux(vector<int>& facilities, const VOL_problem& p,
		const VOL_dvector& x, double& new_icost, double lb);

  // original data for uncapacitated facility location
public: 
  VOL_dvector fcost; // cost for opening facilities
  VOL_dvector dist; // cost for connecting a customer to a facility
  SparseMatrixCSR<double> _dist;
  std::vector<SparseMatrixCSR<double> > _sidecon; // Additional side constr.
  std::vector<double> _ub; // Upper bounds for side constraints
  VOL_dvector fix; // vector saying if some variables should be fixed
  // if fix=-1 nothing is fixed
  int ncust, nloc; // number of customers, number of locations
  int nnz;      // number of nonzero (customer, facility) pairs
  int _p;          // _p>0 for p-median problems 
  VOL_ivector ix;   // best integer feasible solution so far
  double      icost;  // value of best integer feasible solution 
  double ix_sc_viol;  // max violation of any side constraint for ix
  bool have_dummy;    // is there a "dummy" location? (should be fixed)
public:
  UFL() : icost(DBL_MAX), ix_sc_viol(DBL_MAX) {}
  virtual ~UFL() {}  
};

//#############################################################################
//########  Member functions          #########################################
//#############################################################################

//****** UFL_parms
// reading parameters specific to facility location
UFL_parms::UFL_parms(const char *filename) :
   fdata(""), 
   h_iter(10)
{
   char s[500];
   FILE * file = fopen(filename, "r");
   if (!file) { 
      printf("Failure to open ufl datafile: %s\n ", filename);
      abort();
   }
   
   while (fgets(s, 500, file)) {
      const int len = strlen(s) - 1;
      if (s[len] == '\n')
	 s[len] = 0;
      std::string ss;
      ss = s;
      
      if (ss.find("fdata") == 0) {
	 int j = ss.find("=");
	 int j1 = ss.length() - j + 1;
	 fdata = ss.substr(j+1, j1);
	 
      } else if (ss.find("dualfile") == 0) {
	 int j = ss.find("=");
	 int j1 = ss.length() - j + 1;
	 dualfile = ss.substr(j+1, j1);
	 
      } else if (ss.find("dual_savefile") == 0) {
	 int j = ss.find("=");
	 int j1 = ss.length() - j + 1;
	 dual_savefile = ss.substr(j+1, j1);

      } else if (ss.find("int_savefile") == 0) {
	 int j = ss.find("=");
	 int j1 = ss.length() - j + 1;
	 int_savefile = ss.substr(j+1, j1);
	 
      } else if (ss.find("h_iter") == 0) {
	 int i = ss.find("=");  
	 h_iter = atoi(&s[i+1]);
      }	
   }
   fclose(file);
}

#endif
