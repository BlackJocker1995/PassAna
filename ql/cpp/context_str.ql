/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id cpp/example/empty-block
 */

import cpp
import semmle.code.cpp.dataflow.DataFlow



from VariableAccess var, VariableAccess other, FunctionCall call, Function fun, string str, string context
where str = var.getTarget().getName() + var.getTarget().getInitializer().getLocation().toString() and
str in
["ntru_pkey_16file:///opt/src/test_falcon.c:255:35:255:94"]
and
(
//    (
//        DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(other)) and
//        context = other.getTarget().getName().toString()
//    ) or
    (
        DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
        fun = call.getTarget() and
        context = fun.getName()
    )

)

select var.getTarget().getName(), var.getTarget().getInitializer().getLocation(), context

