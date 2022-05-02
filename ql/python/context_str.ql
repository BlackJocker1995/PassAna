/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id python/example/empty-block
 */

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.dataflow.new.DataFlow


from Name var, string str, string context, DataFlow::MethodCallNode method
where str = var.getId() + var.getLocation().toString() and
str in
["EMAIL_PASSWORD/opt/src/sendEmail/EMailClient.py:15"]
and
(
    (
        context = var.getVariable().getAUse().getId()
    ) or
    (
        method.getLocation().toString() = var.getVariable().getALoad().getParentNode().getLocation().toString() and
        context =  method.getMethodName()
    )
)
select var.getId(),var.getLocation().toString(), var.getScope().toString() + context