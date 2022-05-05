/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id java/example/empty-block
 */

import java
import semmle.code.java.dataflow.TaintTracking
import semmle.code.java.dataflow.DataFlow
import DataFlow::PathGraph
import semmle.code.java.dataflow.DataFlow
import semmle.code.java.security.Encryption



from Argument arg, MethodAccess call, VarAccess other, string str, string context
where str = arg.toString() + arg.getLocation().toString() and
str in
["COMPRESSED_FILENAMEfile:///opt/src/src/main/java/com/github/ayltai/gradle/plugin/DownloadTask.java:47:55:47:84"]
and
(
     (
             TaintTracking::localTaint(DataFlow::exprNode(arg), DataFlow::exprNode(other)) and
             context = other.getVariable().getName()
         ) or
         (
             TaintTracking::localTaint(DataFlow::exprNode(arg), DataFlow::exprNode(method_call.getAnArgument())) and
             context = method_call.getQualifier().toString()
         ) or
         (
                 TaintTracking::localTaint(DataFlow::exprNode(arg), DataFlow::exprNode(call.getAnArgument())) and
                 context =  call.getAnArgument().toString()
         )or
         (
                 TaintTracking::localTaint(DataFlow::exprNode(arg), DataFlow::exprNode(call.getAnArgument())) and
                 context =  call.getMethod().getQualifiedName()
         )

)
select arg.toString(), arg.getLocation(), context

