include "globals.mzn";

int : w;
int : n;
array[1..n, 1..2] of int : m;
int : max_h = sum([m[i, 2] | i in 1..n]);

array[1..n] of var 0..w - min([m[i, 1] | i in 1..n]): x;
array[1..n] of var 0..max_h - min([m[i, 2] | i in 1..n]): y;

%optimize
int: area_min = sum([m[i, 2] * m[i,1] | i in 1..n]);
int: min_h = max(max([m[i, 2] | i in 1..n]), floor(area_min/w));
var min_h..max_h : h;

                                             
%no over w, h
constraint forall(i in 1..n) (x[i] + m[i, 1] <= w /\ y[i] + m[i, 2] <= h);
%no overlap 
constraint diffn(x, y, [m[i, 1] | i in 1..n], [m[i, 2] | i in 1..n]);


%cumulative 
constraint cumulative(x, [m[i, 1] | i in 1..n], [m[i,2] | i in 1..n], h);
constraint cumulative(y, [m[i, 2] | i in 1..n], [m[i,1] | i in 1..n], w);


%array[1..n] of int: order = reverse(arg_sort([m[i, 1] | i in 1..n]))
%array[1..n] of int: order = reverse(arg_sort([m[i, 2] | i in 1..n]))
array[1..n] of int: order = reverse(arg_sort([m[i, 1] * max(w + 1, max_h+1) + m[i, 2] | i in 1..n]));
%array[1..n] of int: order = reverse(arg_sort([m[i, 2] * max(w + 1, max_h+1) + m[i, 1] | i in 1..n]));
%array[1..n] of int: order = reverse(arg_sort([m[i, 1]*m[i, 2] | i in 1..n]));

constraint symmetry_breaking_constraint(x[order[1]] = 0 /\ y[order[1]] = 0);

%dual model
array[0..w-1, 0..max_h-1] of var 0..n: b;

%channeling
constraint  forall (i in 0..w-1) ( 
                forall (j in 0..h-1) ( 
                    forall (k in 1..n) (
                        b[i, j] = k <-> x[k] <= i /\ x[k] + m[k, 1] > i /\ y[k] <= j /\ y[k] + m[k, 2] > j
                    )   
                )
            );
            

string: h_var;
string: h_dom;
string: restart;

ann: h_var_ann = 
	if h_var == "dom_w_deg" then
		dom_w_deg
	elseif h_var == "first_fail" then
		first_fail
	else
		input_order
  	endif;
 
ann: h_dom_ann = 
	if h_dom == "indomain_random" then
		indomain_random
	else
		indomain_min
	endif;

ann: restart_ann = 
	if restart == "restart_luby" then
		restart_luby(250)
	elseif restart == "restart_linear" then
		restart_linear(100)
	else
		restart_none
	endif;

ann: search_ann = seq_search([int_search([x[i] | i in order], h_var_ann, h_dom_ann, complete),
                              int_search([y[i] | i in order], h_var_ann, h_dom_ann, complete)]);

ann: search = 
    if restart == "restart_none" then
        search_ann
    else
        seq_search([
            search_ann
            ,restart_ann])
    endif;
solve :: search minimize h;
      
output["\(w) \(h)\n\(n)\n" ++ concat(["\(m[i, 1]) \(m[i, 2]) \(x[i]) \(y[i])\n" | i in 1..n])]