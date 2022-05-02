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



from VarAccess var, MethodAccess method_call, Call call,VarAccess other, string str, string context
where str = var.getVariable().getName() + var.getVariable().getInitializer().getLocation().toString() and
str in
["CASSANDRA_UNIT_KEYSPACEfile:///opt/src/src/test/java/com/mycompany/myapp/AbstractCassandraTest.java:34:58:34:82", "ANONYMOUS_USERfile:///opt/src/src/main/java/com/mycompany/myapp/config/Constants.java:12:49:12:63", "SYSTEM_ACCOUNTfile:///opt/src/src/main/java/com/mycompany/myapp/config/Constants.java:11:49:11:56", "LOGIN_REGEXfile:///opt/src/src/main/java/com/mycompany/myapp/config/Constants.java:9:46:9:66", "ANONYMOUSfile:///opt/src/src/main/java/com/mycompany/myapp/security/AuthoritiesConstants.java:12:44:12:59", "USERfile:///opt/src/src/main/java/com/mycompany/myapp/service/MailService.java:31:40:31:45", "USERfile:///opt/src/src/main/java/com/mycompany/myapp/security/AuthoritiesConstants.java:10:39:10:49", "ADMINfile:///opt/src/src/main/java/com/mycompany/myapp/security/AuthoritiesConstants.java:8:40:8:51", "USERS_BY_EMAIL_CACHEfile:///opt/src/src/main/java/com/mycompany/myapp/repository/UserRepository.java:28:55:28:68", "USERS_BY_LOGIN_CACHEfile:///opt/src/src/main/java/com/mycompany/myapp/repository/UserRepository.java:26:55:26:68", "AUTHORIZATION_HEADERfile:///opt/src/src/main/java/com/mycompany/myapp/security/jwt/JWTConfigurer.java:10:55:10:69", "PROBLEM_BASE_URLfile:///opt/src/src/main/java/com/mycompany/myapp/web/rest/errors/ErrorConstants.java:9:51:9:84", "ERR_VALIDATIONfile:///opt/src/src/main/java/com/mycompany/myapp/web/rest/errors/ErrorConstants.java:8:49:8:66", "ERR_CONCURRENCY_FAILUREfile:///opt/src/src/main/java/com/mycompany/myapp/web/rest/errors/ErrorConstants.java:7:58:7:83", "protocolfile:///opt/src/src/main/java/com/mycompany/myapp/TestApp.java:66:27:66:32", "SPRING_PROFILE_DEFAULTfile:///opt/src/src/main/java/com/mycompany/myapp/config/DefaultProfileUtil.java:17:58:17:82", "ASYNC_LOGSTASH_APPENDER_NAMEfile:///opt/src/src/main/java/com/mycompany/myapp/config/LoggingConfiguration.java:31:64:31:79", "LOGSTASH_APPENDER_NAMEfile:///opt/src/src/main/java/com/mycompany/myapp/config/LoggingConfiguration.java:29:58:29:67", "PROP_METRIC_REG_JCACHE_STATISTICSfile:///opt/src/src/main/java/com/mycompany/myapp/config/MetricsConfiguration.java:35:69:35:87", "PROP_METRIC_REG_JVM_ATTRIBUTE_SETfile:///opt/src/src/main/java/com/mycompany/myapp/config/MetricsConfiguration.java:33:69:33:84", "PROP_METRIC_REG_JVM_BUFFERSfile:///opt/src/src/main/java/com/mycompany/myapp/config/MetricsConfiguration.java:32:63:32:75", "PROP_METRIC_REG_JVM_FILESfile:///opt/src/src/main/java/com/mycompany/myapp/config/MetricsConfiguration.java:31:61:31:71", "PROP_METRIC_REG_JVM_THREADSfile:///opt/src/src/main/java/com/mycompany/myapp/config/MetricsConfiguration.java:30:63:30:75", "PROP_METRIC_REG_JVM_GARBAGEfile:///opt/src/src/main/java/com/mycompany/myapp/config/MetricsConfiguration.java:29:63:29:75", "PROP_METRIC_REG_JVM_MEMORYfile:///opt/src/src/main/java/com/mycompany/myapp/config/MetricsConfiguration.java:28:62:28:73", "activationKeyfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/AccountResourceIntTest.java:388:38:388:58", "jwtfile:///opt/src/src/test/java/com/mycompany/myapp/security/jwt/JWTFilterTest.java:57:22:57:32", "secretKeyfile:///opt/src/src/test/java/com/mycompany/myapp/security/jwt/TokenProviderTest.java:24:38:24:79", "AUTHORITIES_KEYfile:///opt/src/src/main/java/com/mycompany/myapp/security/jwt/TokenProvider.java:25:51:25:56", "BASE_URLfile:///opt/src/src/main/java/com/mycompany/myapp/service/MailService.java:33:44:33:52", "baseUrlfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/util/PaginationUtilUnitTest.java:25:26:25:47", "ENTITY_NAMEfile:///opt/src/src/main/java/com/mycompany/myapp/web/rest/AgentMasterResource.java:30:47:30:59", "PARAMfile:///opt/src/src/main/java/com/mycompany/myapp/web/rest/errors/CustomParameterizedException.java:28:41:28:47", "CASSANDRA_UNIT_RANDOM_PORT_YAMLfile:///opt/src/src/test/java/com/mycompany/myapp/AbstractCassandraTest.java:35:67:35:93", "USER_THREE_EMAILfile:///opt/src/src/test/java/com/mycompany/myapp/security/DomainUserDetailsServiceIntTest.java:37:52:37:78", "USER_THREE_LOGINfile:///opt/src/src/test/java/com/mycompany/myapp/security/DomainUserDetailsServiceIntTest.java:36:52:36:68", "USER_TWO_EMAILfile:///opt/src/src/test/java/com/mycompany/myapp/security/DomainUserDetailsServiceIntTest.java:35:50:35:74", "USER_TWO_LOGINfile:///opt/src/src/test/java/com/mycompany/myapp/security/DomainUserDetailsServiceIntTest.java:34:50:34:64", "USER_ONE_EMAILfile:///opt/src/src/test/java/com/mycompany/myapp/security/DomainUserDetailsServiceIntTest.java:33:50:33:74", "USER_ONE_LOGINfile:///opt/src/src/test/java/com/mycompany/myapp/security/DomainUserDetailsServiceIntTest.java:32:50:32:64", "UPDATED_AGENT_NAMEfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/AgentMasterResourceIntTest.java:48:54:48:65", "DEFAULT_AGENT_NAMEfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/AgentMasterResourceIntTest.java:47:54:47:65", "UPDATED_LASTNAMEfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:66:52:66:69", "UPDATED_FIRSTNAMEfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:63:53:63:71", "DEFAULT_FIRSTNAMEfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:62:53:62:58", "UPDATED_EMAILfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:60:49:60:68", "DEFAULT_EMAILfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:59:49:59:67", "UPDATED_PASSWORDfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:57:52:57:65", "DEFAULT_PASSWORDfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:56:52:56:64", "UPDATED_LOGINfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:52:49:52:58", "DEFAULT_LOGINfile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/UserResourceIntTest.java:51:49:51:57", "expectedDatafile:///opt/src/src/test/java/com/mycompany/myapp/web/rest/util/PaginationUtilUnitTest.java:34:31:37:72"]
and
(
    (
        TaintTracking::localTaint(DataFlow::exprNode(var), DataFlow::exprNode(other)) and
        context = other.getVariable().getName()
    ) or
    (
        TaintTracking::localTaint(DataFlow::exprNode(var), DataFlow::exprNode(method_call.getAnArgument())) and
        context = method_call.getQualifier().toString()
    ) or
    (
            TaintTracking::localTaint(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
            context =  call.getAnArgument().toString()
    )or
    (
            TaintTracking::localTaint(DataFlow::exprNode(var), DataFlow::exprNode(call.getAnArgument())) and
            context =  call.getMethod().getQualifiedName()
    )

)
select var.getVariable().getName(), var.getVariable().getInitializer().getLocation(), context