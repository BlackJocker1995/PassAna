/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id csharp/example/empty-block
 */

import csharp


from VariableAccess var, VariableAccess other, Call call, MethodCall method_call, string str, string context
where str = var.getTarget().getName() + var.getTarget().getInitializer().getLocation().toString() and
str in
["BF_ALL/opt/src/Program.cs:73:13:73:30", "BF_GS1_DATABAR/opt/src/Program.cs:79:13:79:39", "BF_POSTALCODE/opt/src/Program.cs:82:13:82:38", "BF_GS1_DATABAR_LIMITED/opt/src/Program.cs:136:13:136:44", "BF_PATCHCODE/opt/src/Program.cs:139:13:139:37", "BF_USPSINTELLIGENTMAIL/opt/src/Program.cs:142:13:142:47", "BF_POSTNET/opt/src/Program.cs:145:13:145:35", "BF_PLANET/opt/src/Program.cs:148:13:148:34", "BF_AUSTRALIANPOST/opt/src/Program.cs:151:13:151:42", "BF_UKROYALMAIL/opt/src/Program.cs:154:13:154:39", "BF_PDF417/opt/src/Program.cs:157:13:157:34", "BF_QR_CODE/opt/src/Program.cs:160:13:160:35", "BF_DATAMATRIX/opt/src/Program.cs:163:13:163:38", "BF_AZTEC/opt/src/Program.cs:166:13:166:33", "BF_MAXICODE/opt/src/Program.cs:169:13:169:36", "BF_MICRO_QR/opt/src/Program.cs:172:13:172:36", "BF_MICRO_PDF417/opt/src/Program.cs:175:13:175:40", "BF_GS1_COMPOSITE/opt/src/Program.cs:178:13:178:42"]
and
(
    (
        TaintTracking::localTaint(DataFlow::exprNode(var), DataFlow::exprNode(other)) and
        context = other.getTarget().getName()
    ) or
    (
        DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
        context = call.getTarget().getName()
    )
    or
        (
            DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
            context = call.getAnArgument().toString()
        )
    or
    (
        DataFlow::localFlow(DataFlow::exprNode(var), DataFlow::exprNode(method_call.getAnArgument())) and
        context = method_call.getQualifier().toString()
    )
)
select var.getTarget().getName(), var.getTarget().getInitializer().getLocation(), context