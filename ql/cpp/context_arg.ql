/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id cpp/example/empty-block
 */

import cpp
import semmle.code.cpp.dataflow.DataFlow


from StringLiteral str_var, VariableAccess other, Call call,  string str, string context
where str_var = call.getAnArgument() and
str = str_var.toString() + str_var.getLocation().toString() and
str in
["Not enough memory!file:///opt/src/src/modloaders/ft2_load_digi.c:97:17:97:36"]
and
(
    (
          DataFlow::localFlow(DataFlow::exprNode(str_var), DataFlow::exprNode(other)) and
          context = other.getTarget().getName().toString() 
      ) or
       (
           DataFlow::localFlow(DataFlow::exprNode(str_var), DataFlow::exprNode(call.getAnArgument())) and
           context = call.getAnArgument().toString() and 
           context != str_var.toString()
       )
       or
       (
           DataFlow::localFlow(DataFlow::exprNode(str_var), DataFlow::exprNode(call.getAnArgument())) and
           context = call.getAPredecessor().toString()
       )
       //or
    //    (
    //        DataFlow::localFlow(DataFlow::exprNode(str_var), DataFlow::exprNode(call.getAnArgument())) and
    //        context = call.getTarget().getName()
    //    )

)
select str_var.toString(), str_var.getLocation(), context