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
["SECRET_KEY/opt/src/setting.py:6", "AppSecret/opt/src/setting.py:13"]
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


// //	/opt/src/tripleo_ansible/tests/plugins/filter/test_helpers.py:380
// class RegularNode extends DataFlow::ExprNode{
//     RegularNode(){
//         exists(Call call, Name name|
//             this.asExpr().(Name)= name or this.asExpr().(Call) = call)

//     }
// }

// class DataConfig extends TaintTracking::Configuration {
//     DataConfig() { this = "<some unique identifier>" }
//     override predicate isSource(DataFlow::Node nd) {
//       nd instanceof GetPass
//     }
//     override predicate isSink(DataFlow::Node nd) {
//         nd instanceof RegularNode
//     }
// }

// from DataConfig cfg, DataFlow::PathNode source, DataFlow::PathNode sink, string str
// where cfg.hasFlowPath(source, sink) and (str = sink.getNode().asExpr().(Name).getId() or str = sink.getNode().asExpr().(Call).getFunc().getASubExpression().toString())
// select
// source.getNode().asExpr().(Unicode).getText(), source.getNode().getLocation(),
// str, sink.getNode().getScope().getName()

