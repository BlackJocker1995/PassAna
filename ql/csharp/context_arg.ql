/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id csharp/example/empty-block
 */

import csharp


from MethodCall method_call, StringLiteral str_var, VariableAccess other, Call call,  string str, string context
where str_var = call.getAnArgument() and
str = str_var.toString() + str_var.getLocation().toString() and str in
["mRemoteServer/opt/src/Source/MSBuild.Community.Tasks.Tests/IIS/WebDirectoryCreateTest.cs:17:34:17:41"]
and
(
    (
            TaintTracking::localTaint(DataFlow::exprNode(str_var), DataFlow::exprNode(other)) and
            context = other.getTarget().getName()
        ) or
        (
            DataFlow::localFlow(DataFlow::exprNode(str_var), DataFlow::exprNode(call.getAnArgument())) and
            context = call.getTarget().getName()
        )
        or
            (
                DataFlow::localFlow(DataFlow::exprNode(str_var), DataFlow::exprNode(call.getAnArgument())) and
                context = call.getAnArgument().toString()
            )
        or
        (
            DataFlow::localFlow(DataFlow::exprNode(str_var), DataFlow::exprNode(method_call.getAnArgument())) and
            context = method_call.getQualifier().toString()
        )

)
select str_var.toString(), str_var.toString(), str_var.getLocation().toString(), context