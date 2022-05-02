/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id cpp/example/empty-block
 */

import cpp
import semmle.code.cpp.dataflow.DataFlow



from VariableAccess var, VariableAccess other, Call call, string str, string context
where str = var.getTarget().getName() + var.getTarget().getInitializer().getLocation().toString() and
str in
["zFormatfile:///opt/src/native/sqlite3/sqlite3.c:135302:28:135302:75", "zInfile:///opt/src/native/sqlite3/sqlite3.c:95962:22:95962:51", "zErrfile:///opt/src/native/sqlite3/sqlite3.c:156553:21:156553:36", "hexdigitsfile:///opt/src/native/db.c:513:39:513:56", "zRetfile:///opt/src/native/sqlite3/sqlite3.c:122172:23:122172:31", "zFmtfile:///opt/src/native/sqlite3/sqlite3.c:99755:21:99755:66", "pow63file:///opt/src/native/sqlite3/sqlite3.c:30833:22:30833:42"]
and
(
   (
       DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(other)) and
       context = other.getTarget().getName().toString()
   ) or
    (
        DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
        context = call.getAnArgument().toString()
    )or
    (
        DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
        context = call.getQualifier().toString()
    )or
    (
        DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
        context = call.getTarget().getName()
    )

)

select var.getTarget().getName(), var.getTarget().getInitializer().getLocation(), context

