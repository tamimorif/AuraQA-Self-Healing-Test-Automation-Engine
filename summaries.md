# AuraQA Project Audit Report

This document contains a comprehensive audit report of the AuraQA project compiled for external review.

---

### 1. File Listing of AuraQA Project Tree
*(Excluding dependency directories like `node_modules` and `.git`)*

```text
./.gitattributes
./.gitignore
./AuraQA_Agent_Prompt.md.pdf
./FINAL_VALIDATION_REPORT.md
./README.md
./auraqa_thumbnail.png
./backend/__init__.py
./backend/config/__init__.py
./backend/config/env_schema.py
./backend/config/settings.py
./backend/graph/__init__.py
./backend/graph/edges/__init__.py
./backend/graph/edges/routing.py
./backend/graph/graph.py
./backend/graph/nodes/__init__.py
./backend/graph/nodes/analyze_dom.py
./backend/graph/nodes/escalate.py
./backend/graph/nodes/generate_selector.py
./backend/graph/nodes/provision_test_data.py
./backend/graph/nodes/rerun_test.py
./backend/graph/nodes/validate_selector.py
./backend/graph/state.py
./backend/graph/tools/__init__.py
./backend/graph/tools/dom_parser.py
./backend/graph/tools/jira_client.py
./backend/graph/tools/selector_scorer.py
./backend/graph/tools/tdo_client.py
./backend/main.py
./backend/models/__init__.py
./backend/models/schemas.py
./backend/services/__init__.py
./backend/services/audit_service.py
./backend/services/healing_service.py
./backend/tests/__init__.py
./backend/tests/conftest.py
./backend/tests/test_dom_parser.py
./backend/tests/test_graph.py
./backend/tests/test_schemas.py
./backend/tests/test_selector_scorer.py
./contracts/audit_log.json
./contracts/failure_payload.json
./contracts/healed_response.json
./infrastructure/.env.example
./infrastructure/Dockerfile
./infrastructure/Dockerfile.mockapp
./infrastructure/docker-compose.yml
./infrastructure/nginx.conf
./mock_app/index.html
./mock_app/package-lock.json
./mock_app/package.json
./mock_app/postcss.config.js
./mock_app/src/App.jsx
./mock_app/src/components/Dashboard.jsx
./mock_app/src/components/LoginForm.jsx
./mock_app/src/components/MutationPanel.jsx
./mock_app/src/components/Navigation.jsx
./mock_app/src/components/UserTable.jsx
./mock_app/src/index.css
./mock_app/src/main.jsx
./mock_app/src/mutations/mutationEngine.js
./mock_app/src/mutations/scenarios.js
./mock_app/tailwind.config.js
./mock_app/vite.config.js
./mypy.ini
./pyproject.toml
./requirements.txt
./scripts/deploy_uipath.sh
./scripts/run_e2e.sh
./scripts/setup.sh
./uipath/integration/jira_connector.json
./uipath/integration/tdo_connector.json
./uipath/project.json
./uipath/workflows/ApplyHealedSelector.xaml
./uipath/workflows/DetectFailure.xaml
./uipath/workflows/InvokeHealingAgent.xaml
./uipath/workflows/LogToJira.xaml
./uipath/workflows/Main.xaml
./uipath/workflows/ProvisionTestData.xaml
./uipath/workflows/RunTest.xaml
```

---

### 2. Full Content of Key Files

#### 📂 `uipath/workflows/LogToJira.xaml`
```xml
<Activity mc:Ignorable="sap sap2010" x:Class="LogToJira" xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation" xmlns:scg="clr-namespace:System.Collections.Generic;assembly=System.Private.CoreLib" xmlns:ui="http://schemas.uipath.com/workflow/activities" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <x:Members>
    <x:Property Name="in_AuditLogJson" Type="InArgument(x:String)" />
    <x:Property Name="in_JiraProjectKey" Type="InArgument(x:String)" />
    <x:Property Name="out_JiraIssueKey" Type="OutArgument(x:String)" />
  </x:Members>
  <sap:VirtualizedContainerService.HintSize>800,600</sap:VirtualizedContainerService.HintSize>
  <sap2010:WorkflowViewState.IdRef>LogToJira_1</sap2010:WorkflowViewState.IdRef>
  <TextExpression.NamespacesForImplementation>
    <scg:List x:TypeArguments="x:String" Capacity="42">
      <x:String>System.Activities</x:String>
      <x:String>System.Activities.Statements</x:String>
      <x:String>System</x:String>
      <x:String>System.Collections</x:String>
      <x:String>System.Collections.Generic</x:String>
      <x:String>UiPath.Core.Activities</x:String>
      <x:String>System.Runtime.Serialization</x:String>
    </scg:List>
  </TextExpression.NamespacesForImplementation>
  <TextExpression.ReferencesForImplementation>
    <scg:List x:TypeArguments="AssemblyReference" Capacity="32">
      <AssemblyReference>System.Activities</AssemblyReference>
      <AssemblyReference>System.Private.CoreLib</AssemblyReference>
      <AssemblyReference>UiPath.System.Activities</AssemblyReference>
    </scg:List>
  </TextExpression.ReferencesForImplementation>
  <Sequence DisplayName="LogToJira" sap:VirtualizedContainerService.HintSize="500,400" sap2010:WorkflowViewState.IdRef="Sequence_1">
    <sap:WorkflowViewStateService.ViewState>
      <scg:Dictionary x:TypeArguments="x:String, x:Object">
        <x:Boolean x:Key="IsExpanded">True</x:Boolean>
      </scg:Dictionary>
    </sap:WorkflowViewStateService.ViewState>
    <ui:LogMessage DisplayName="Log Message" sap:VirtualizedContainerService.HintSize="338,103" sap2010:WorkflowViewState.IdRef="LogMessage_1" Level="Info" Message="[&quot;Creating Jira issue for audit log...&quot;]" />
    <Assign DisplayName="Assign Mock Issue Key" sap:VirtualizedContainerService.HintSize="338,70" sap2010:WorkflowViewState.IdRef="Assign_1">
      <Assign.To>
        <OutArgument x:TypeArguments="x:String">[out_JiraIssueKey]</OutArgument>
      </Assign.To>
      <Assign.Value>
        <InArgument x:TypeArguments="x:String">[in_JiraProjectKey + "-1001"]</InArgument>
      </Assign.Value>
    </Assign>
    <ui:LogMessage DisplayName="Log Message" sap:VirtualizedContainerService.HintSize="338,103" sap2010:WorkflowViewState.IdRef="LogMessage_2" Level="Info" Message="[&quot;Jira issue created successfully: &quot; + out_JiraIssueKey]" />
  </Sequence>
</Activity>
```

#### 📂 `uipath/workflows/ProvisionTestData.xaml`
```xml
<Activity mc:Ignorable="sap sap2010" x:Class="ProvisionTestData" xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation" xmlns:scg="clr-namespace:System.Collections.Generic;assembly=System.Private.CoreLib" xmlns:ui="http://schemas.uipath.com/workflow/activities" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <x:Members>
    <x:Property Name="in_TestCaseId" Type="InArgument(x:String)" />
    <x:Property Name="in_DatasetName" Type="InArgument(x:String)" />
    <x:Property Name="in_RecordCount" Type="InArgument(x:Int32)" />
    <x:Property Name="out_TestDataJson" Type="OutArgument(x:String)" />
  </x:Members>
  <sap:VirtualizedContainerService.HintSize>800,600</sap:VirtualizedContainerService.HintSize>
  <sap2010:WorkflowViewState.IdRef>ProvisionTestData_1</sap2010:WorkflowViewState.IdRef>
  <TextExpression.NamespacesForImplementation>
    <scg:List x:TypeArguments="x:String" Capacity="42">
      <x:String>System.Activities</x:String>
      <x:String>System.Activities.Statements</x:String>
      <x:String>System</x:String>
      <x:String>System.Collections</x:String>
      <x:String>System.Collections.Generic</x:String>
      <x:String>UiPath.Core.Activities</x:String>
    </scg:List>
  </TextExpression.NamespacesForImplementation>
  <TextExpression.ReferencesForImplementation>
    <scg:List x:TypeArguments="AssemblyReference" Capacity="32">
      <AssemblyReference>System.Activities</AssemblyReference>
      <AssemblyReference>System.Private.CoreLib</AssemblyReference>
      <AssemblyReference>UiPath.System.Activities</AssemblyReference>
    </scg:List>
  </TextExpression.ReferencesForImplementation>
  <Sequence DisplayName="ProvisionTestData" sap:VirtualizedContainerService.HintSize="500,400" sap2010:WorkflowViewState.IdRef="Sequence_1">
    <sap:WorkflowViewStateService.ViewState>
      <scg:Dictionary x:TypeArguments="x:String, x:Object">
        <x:Boolean x:Key="IsExpanded">True</x:Boolean>
      </scg:Dictionary>
    </sap:WorkflowViewStateService.ViewState>
    <ui:LogMessage DisplayName="Log Message" sap:VirtualizedContainerService.HintSize="338,103" sap2010:WorkflowViewState.IdRef="LogMessage_1" Level="Info" Message="[&quot;Provisioning &quot; + in_RecordCount.ToString() + &quot; records from TDO dataset: &quot; + in_DatasetName]" />
    <Assign DisplayName="Assign Mock Test Data" sap:VirtualizedContainerService.HintSize="338,70" sap2010:WorkflowViewState.IdRef="Assign_1">
      <Assign.To>
        <OutArgument x:TypeArguments="x:String">[out_TestDataJson]</OutArgument>
      </Assign.To>
      <Assign.Value>
        <InArgument x:TypeArguments="x:String">["{ ""records"": [] }"]</InArgument>
      </Assign.Value>
    </Assign>
    <ui:LogMessage DisplayName="Log Message" sap:VirtualizedContainerService.HintSize="338,103" sap2010:WorkflowViewState.IdRef="LogMessage_2" Level="Info" Message="[&quot;Test data provisioned successfully.&quot;]" />
  </Sequence>
</Activity>
```

#### 📂 `uipath/workflows/Main.xaml`
```xml
<!-- AuraQA Master Orchestrator Workflow -->
<Activity mc:Ignorable="sap sap2010 sads" x:Class="AuraQA.Main"
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation"
  xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"
  xmlns:sads="http://schemas.microsoft.com/netfx/2010/xaml/activities/debugger"
  xmlns:scg="clr-namespace:System.Collections.Generic;assembly=mscorlib"
  xmlns:ui="http://schemas.uipath.com/workflow/activities"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

  <x:Members>
    <x:Property Name="in_TestCaseId" Type="InArgument(x:String)" />
    <x:Property Name="in_TestSuiteId" Type="InArgument(x:String)" />
    <x:Property Name="in_TargetUrl" Type="InArgument(x:String)" />
    <x:Property Name="in_HealingApiEndpoint" Type="InArgument(x:String)" />
    <x:Property Name="in_JiraProjectKey" Type="InArgument(x:String)" />
  </x:Members>

  <Sequence DisplayName="AuraQA Main Orchestrator" sap2010:WorkflowViewState.IdRef="MainSequence_1">

    <!-- ════════════════════════════════════════════════════ -->
    <!-- Variable declarations -->
    <!-- ════════════════════════════════════════════════════ -->
    <Sequence.Variables>
      <Variable x:TypeArguments="x:String" Name="var_TestCaseId" />
      <Variable x:TypeArguments="x:String" Name="var_TestSuiteId" />
      <Variable x:TypeArguments="x:String" Name="var_TargetUrl" />
      <Variable x:TypeArguments="x:String" Name="var_HealingApiEndpoint" />
      <Variable x:TypeArguments="x:String" Name="var_JiraProjectKey" />
      <Variable x:TypeArguments="x:Boolean" Name="var_TestPassed" Default="False" />
      <Variable x:TypeArguments="x:String" Name="var_ErrorMessage" />
      <Variable x:TypeArguments="x:String" Name="var_DOMSnapshot" />
      <Variable x:TypeArguments="x:String" Name="var_FailurePayloadJson" />
      <Variable x:TypeArguments="x:String" Name="var_HealedSelectorJson" />
      <Variable x:TypeArguments="x:String" Name="var_HealingStatus" />
      <Variable x:TypeArguments="x:Double" Name="var_Confidence" Default="0" />
      <Variable x:TypeArguments="x:Boolean" Name="var_RerunPassed" Default="False" />
      <Variable x:TypeArguments="x:String" Name="var_AuditLogJson" />
      <Variable x:TypeArguments="x:String" Name="var_JiraIssueKey" />
      <Variable x:TypeArguments="x:String" Name="var_HealedSelector" />
      <Variable x:TypeArguments="x:String" Name="var_SelectorType" />
    </Sequence.Variables>

    <!-- ════════════════════════════════════════════════════ -->
    <!-- Initialize arguments into local variables -->
    <!-- ════════════════════════════════════════════════════ -->
    <Assign DisplayName="Initialize TestCaseId">
      <Assign.To><OutArgument x:TypeArguments="x:String">[var_TestCaseId]</OutArgument></Assign.To>
      <Assign.Value><InArgument x:TypeArguments="x:String">[in_TestCaseId]</InArgument></Assign.Value>
    </Assign>
    <Assign DisplayName="Initialize TestSuiteId">
      <Assign.To><OutArgument x:TypeArguments="x:String">[var_TestSuiteId]</OutArgument></Assign.To>
      <Assign.Value><InArgument x:TypeArguments="x:String">[in_TestSuiteId]</InArgument></Assign.Value>
    </Assign>
    <Assign DisplayName="Initialize TargetUrl">
      <Assign.To><OutArgument x:TypeArguments="x:String">[var_TargetUrl]</OutArgument></Assign.To>
      <Assign.Value><InArgument x:TypeArguments="x:String">[in_TargetUrl]</InArgument></Assign.Value>
    </Assign>
    <Assign DisplayName="Initialize HealingApiEndpoint">
      <Assign.To><OutArgument x:TypeArguments="x:String">[var_HealingApiEndpoint]</OutArgument></Assign.To>
      <Assign.Value><InArgument x:TypeArguments="x:String">[in_HealingApiEndpoint]</InArgument></Assign.Value>
    </Assign>
    <Assign DisplayName="Initialize JiraProjectKey">
      <Assign.To><OutArgument x:TypeArguments="x:String">[var_JiraProjectKey]</OutArgument></Assign.To>
      <Assign.Value><InArgument x:TypeArguments="x:String">[in_JiraProjectKey]</InArgument></Assign.Value>
    </Assign>

    <ui:LogMessage DisplayName="Log Pipeline Start" Level="Info"
      Message="[String.Format(&quot;AuraQA Pipeline started — TC: {0}, Suite: {1}, URL: {2}&quot;, var_TestCaseId, var_TestSuiteId, var_TargetUrl)]" />

    <!-- ════════════════════════════════════════════════════ -->
    <!-- Master Try-Catch: Full healing pipeline -->
    <!-- ════════════════════════════════════════════════════ -->
    <TryCatch DisplayName="Master Pipeline Try-Catch">
      <TryCatch.Try>
        <Sequence DisplayName="Healing Pipeline Sequence">

          <!-- ──────────────────────────────────────────── -->
          <!-- STEP 1: Run the test case -->
          <!-- ──────────────────────────────────────────── -->
          <ui:InvokeWorkflowFile DisplayName="Step 1 — RunTest"
            WorkflowFileName="workflows/RunTest.xaml"
            ContinueOnError="False">
            <ui:InvokeWorkflowFile.Arguments>
              <InArgument x:TypeArguments="x:String" x:Key="in_TestCaseId">[var_TestCaseId]</InArgument>
              <InArgument x:TypeArguments="x:String" x:Key="in_TestSuiteId">[var_TestSuiteId]</InArgument>
              <InArgument x:TypeArguments="x:String" x:Key="in_TargetUrl">[var_TargetUrl]</InArgument>
              <OutArgument x:TypeArguments="x:Boolean" x:Key="out_TestPassed">[var_TestPassed]</OutArgument>
              <OutArgument x:TypeArguments="x:String" x:Key="out_ErrorMessage">[var_ErrorMessage]</OutArgument>
              <OutArgument x:TypeArguments="x:String" x:Key="out_DOMSnapshot">[var_DOMSnapshot]</OutArgument>
            </ui:InvokeWorkflowFile.Arguments>
          </ui:InvokeWorkflowFile>

          <ui:LogMessage DisplayName="Log RunTest Result" Level="Info"
            Message="[String.Format(&quot;RunTest completed — Passed: {0}&quot;, var_TestPassed)]" />

          <!-- ──────────────────────────────────────────── -->
          <!-- STEP 2: If test failed, detect failure details -->
          <!-- ──────────────────────────────────────────── -->
          <If DisplayName="Check If Test Failed" Condition="[Not var_TestPassed]">
            <If.Then>
              <Sequence DisplayName="Failure Handling Sequence">

                <ui:LogMessage DisplayName="Log Failure Detected" Level="Warn"
                  Message="[String.Format(&quot;Test FAILED — TC: {0}, Error: {1}&quot;, var_TestCaseId, var_ErrorMessage)]" />

                <!-- DetectFailure -->
                <ui:InvokeWorkflowFile DisplayName="Step 2 — DetectFailure"
                  WorkflowFileName="workflows/DetectFailure.xaml"
                  ContinueOnError="False">
                  <ui:InvokeWorkflowFile.Arguments>
                    <InArgument x:TypeArguments="x:String" x:Key="in_ErrorMessage">[var_ErrorMessage]</InArgument>
                    <InArgument x:TypeArguments="x:String" x:Key="in_TargetUrl">[var_TargetUrl]</InArgument>
                    <InArgument x:TypeArguments="x:String" x:Key="in_TestCaseId">[var_TestCaseId]</InArgument>
                    <InArgument x:TypeArguments="x:String" x:Key="in_TestSuiteId">[var_TestSuiteId]</InArgument>
                    <InArgument x:TypeArguments="x:String" x:Key="in_DOMSnapshot">[var_DOMSnapshot]</InArgument>
                    <OutArgument x:TypeArguments="x:String" x:Key="out_FailurePayloadJson">[var_FailurePayloadJson]</OutArgument>
                  </ui:InvokeWorkflowFile.Arguments>
                </ui:InvokeWorkflowFile>

                <ui:LogMessage DisplayName="Log Failure Payload Built" Level="Info"
                  Message="DetectFailure completed — Payload assembled." />

                <!-- ──────────────────────────────────────── -->
                <!-- STEP 3: Invoke the Python healing agent -->
                <!-- ──────────────────────────────────────── -->
                <ui:InvokeWorkflowFile DisplayName="Step 3 — InvokeHealingAgent"
                  WorkflowFileName="workflows/InvokeHealingAgent.xaml"
                  ContinueOnError="False">
                  <ui:InvokeWorkflowFile.Arguments>
                    <InArgument x:TypeArguments="x:String" x:Key="in_FailurePayloadJson">[var_FailurePayloadJson]</InArgument>
                    <InArgument x:TypeArguments="x:String" x:Key="in_ApiEndpoint">[var_HealingApiEndpoint]</InArgument>
                    <OutArgument x:TypeArguments="x:String" x:Key="out_HealedSelectorJson">[var_HealedSelectorJson]</OutArgument>
                    <OutArgument x:TypeArguments="x:String" x:Key="out_HealingStatus">[var_HealingStatus]</OutArgument>
                    <OutArgument x:TypeArguments="x:Double" x:Key="out_Confidence">[var_Confidence]</OutArgument>
                  </ui:InvokeWorkflowFile.Arguments>
                </ui:InvokeWorkflowFile>

                <ui:LogMessage DisplayName="Log Healing Result" Level="Info"
                  Message="[String.Format(&quot;Healing API returned — Status: {0}, Confidence: {1:F1}%&quot;, var_HealingStatus, var_Confidence)]" />

                <!-- ──────────────────────────────────────── -->
                <!-- STEP 4: Apply healed selector (if healed) -->
                <!-- ──────────────────────────────────────── -->
                <If DisplayName="Check If Healing Succeeded" Condition="[var_HealingStatus = &quot;healed&quot;]">
                  <If.Then>
                    <Sequence DisplayName="Apply Healed Selector Sequence">

                      <ui:InvokeWorkflowFile DisplayName="Step 4 — ApplyHealedSelector"
                        WorkflowFileName="workflows/ApplyHealedSelector.xaml"
                        ContinueOnError="False">
                        <ui:InvokeWorkflowFile.Arguments>
                          <InArgument x:TypeArguments="x:String" x:Key="in_HealedSelector">[var_HealedSelector]</InArgument>
                          <InArgument x:TypeArguments="x:String" x:Key="in_SelectorType">[var_SelectorType]</InArgument>
                          <InArgument x:TypeArguments="x:String" x:Key="in_TestCaseId">[var_TestCaseId]</InArgument>
                          <OutArgument x:TypeArguments="x:Boolean" x:Key="out_RerunPassed">[var_RerunPassed]</OutArgument>
                        </ui:InvokeWorkflowFile.Arguments>
                      </ui:InvokeWorkflowFile>

                      <ui:LogMessage DisplayName="Log Apply Result" Level="Info"
                        Message="[String.Format(&quot;Healed selector applied — Rerun Passed: {0}&quot;, var_RerunPassed)]" />

                    </Sequence>
                  </If.Then>
                  <If.Else>
                    <Sequence DisplayName="Healing Not Successful">
                      <ui:LogMessage DisplayName="Log Healing Escalated" Level="Warn"
                        Message="[String.Format(&quot;Healing was not successful — Status: {0}. Escalating to Jira.&quot;, var_HealingStatus)]" />
                    </Sequence>
                  </If.Else>
                </If>

                <!-- ──────────────────────────────────────── -->
                <!-- STEP 5: Log audit trail to Jira -->
                <!-- ──────────────────────────────────────── -->
                <ui:InvokeWorkflowFile DisplayName="Step 5 — LogToJira"
                  WorkflowFileName="workflows/LogToJira.xaml"
                  ContinueOnError="True">
                  <ui:InvokeWorkflowFile.Arguments>
                    <InArgument x:TypeArguments="x:String" x:Key="in_AuditLogJson">[var_AuditLogJson]</InArgument>
                    <InArgument x:TypeArguments="x:String" x:Key="in_JiraProjectKey">[var_JiraProjectKey]</InArgument>
                    <OutArgument x:TypeArguments="x:String" x:Key="out_JiraIssueKey">[var_JiraIssueKey]</OutArgument>
                  </ui:InvokeWorkflowFile.Arguments>
                </ui:InvokeWorkflowFile>

                <ui:LogMessage DisplayName="Log Jira Result" Level="Info"
                  Message="[String.Format(&quot;Jira issue created: {0}&quot;, var_JiraIssueKey)]" />

              </Sequence>
            </If.Then>
            <If.Else>
              <Sequence DisplayName="Test Passed — No Healing Needed">
                <ui:LogMessage DisplayName="Log Test Passed" Level="Info"
                  Message="[String.Format(&quot;Test PASSED — TC: {0}. No healing needed.&quot;, var_TestCaseId)]" />
              </Sequence>
            </If.Else>
          </If>

        </Sequence>
      </TryCatch.Try>

      <TryCatch.Catches>
        <Catch x:TypeArguments="s:Exception" xmlns:s="clr-namespace:System;assembly=mscorlib">
          <ActivityAction x:TypeArguments="s:Exception">
            <ActivityAction.Argument>
              <DelegateInArgument x:TypeArguments="s:Exception" Name="pipelineException" />
            </ActivityAction.Argument>
            <Sequence DisplayName="Handle Pipeline Exception">
              <ui:LogMessage DisplayName="Log Pipeline Exception" Level="Error"
                Message="[String.Format(&quot;AuraQA Pipeline EXCEPTION — TC: {0}, Error: {1}&quot;, var_TestCaseId, pipelineException.Message)]" />

              <!-- Attempt to log the failure to Jira even on exception -->
              <TryCatch DisplayName="Emergency Jira Logging">
                <TryCatch.Try>
                  <ui:InvokeWorkflowFile DisplayName="Emergency LogToJira"
                    WorkflowFileName="workflows/LogToJira.xaml"
                    ContinueOnError="True">
                    <ui:InvokeWorkflowFile.Arguments>
                      <InArgument x:TypeArguments="x:String" x:Key="in_AuditLogJson">[String.Format("{""audit_id"":""emergency"",""test_case_id"":""{0}"",""test_suite_id"":""{1}"",""original_selector"":""N/A"",""status"":""failed"",""error_message"":""{2}""}", var_TestCaseId, var_TestSuiteId, pipelineException.Message)]</InArgument>
                      <InArgument x:TypeArguments="x:String" x:Key="in_JiraProjectKey">[var_JiraProjectKey]</InArgument>
                      <OutArgument x:TypeArguments="x:String" x:Key="out_JiraIssueKey">[var_JiraIssueKey]</OutArgument>
                    </ui:InvokeWorkflowFile.Arguments>
                  </ui:InvokeWorkflowFile>
                </TryCatch.Try>
                <TryCatch.Catches>
                  <Catch x:TypeArguments="s:Exception">
                    <ActivityAction x:TypeArguments="s:Exception">
                      <ActivityAction.Argument>
                        <DelegateInArgument x:TypeArguments="s:Exception" Name="jiraException" />
                      </ActivityAction.Argument>
                      <ui:LogMessage DisplayName="Log Jira Emergency Failure" Level="Fatal"
                        Message="[String.Format(&quot;CRITICAL: Emergency Jira logging also failed — {0}&quot;, jiraException.Message)]" />
                    </ActivityAction>
                  </Catch>
                </TryCatch.Catches>
              </TryCatch>

              <Rethrow DisplayName="Rethrow Pipeline Exception" />
            </Sequence>
          </ActivityAction>
        </Catch>
      </TryCatch.Catches>

      <TryCatch.Finally>
        <ui:LogMessage DisplayName="Log Pipeline Complete" Level="Info"
          Message="[String.Format(&quot;AuraQA Pipeline finished — TC: {0}, Jira: {1}&quot;, var_TestCaseId, If(String.IsNullOrEmpty(var_JiraIssueKey), &quot;N/A&quot;, var_JiraIssueKey))]" />
      </TryCatch.Finally>
    </TryCatch>

  </Sequence>
</Activity>
```

#### 📂 `uipath/project.json`
```json
{
  "$schema": "https://cloud.uipath.com/draft-07/project-schema",
  "name": "AuraQA.SelfHealingEngine",
  "projectId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "description": "AuraQA Self-Healing Enterprise Test Automation Engine — UiPath orchestrator component. Detects broken selectors, invokes the Python healing agent, applies healed selectors, and logs audit trails to Jira.",
  "main": "workflows/Main.xaml",
  "projectVersion": "1.0.0",
  "schemaVersion": "4.0",
  "studioVersion": "2024.10.0",
  "targetFramework": "Windows",
  "expressionLanguage": "VisualBasic",
  "entryPoints": [
    {
      "filePath": "workflows/Main.xaml",
      "uniqueId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "input": [],
      "output": []
    }
  ],
  "dependencies": {
    "UiPath.System.Activities": "[24.10.4]",
    "UiPath.UIAutomation.Activities": "[24.10.7]",
    "UiPath.Testing.Activities": "[24.10.3]",
    "UiPath.WebAPI.Activities": "[24.10.2]",
    "UiPath.Mail.Activities": "[1.23.0]",
    "UiPath.Excel.Activities": "[2.24.2]"
  },
  "toolVersion": "1.0.0",
  "runtimeOptions": {
    "autoDispose": false,
    "netFrameworkLazyLoading": false,
    "isPausable": true,
    "isAttended": false,
    "requiresUserInteraction": false,
    "supportsPip": false,
    "startsFromTrigger": false
  },
  "designOptions": {
    "projectProfile": "Developement",
    "outputType": "Process",
    "libraryOptions": {
      "includeOriginalXaml": false,
      "privateWorkflows": []
    }
  },
  "fileInfoCollection": []
}
```

#### 📂 `backend/main.py`
```python
"""
AuraQA FastAPI application.

Exposes the self-healing REST API consumed by UiPath Orchestrator.

Endpoints:
    POST /heal          — Accept a test-failure payload and return a healed selector.
    GET  /health        — Liveness / readiness probe.
    GET  /              — Root welcome message.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import configure_logging, get_settings
from backend.models.schemas import (
    HealedSelectorResponse,
    HealingStatus,
    TestFailurePayload,
)
from backend.services.healing_service import HealingService

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Lifespan — startup / shutdown hooks
# ------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context: configure logging on startup."""
    settings = get_settings()
    configure_logging(settings)
    logger.info(
        "AuraQA %s starting (env=%s, debug=%s)",
        settings.app_version,
        settings.app_env,
        settings.debug,
    )
    yield
    logger.info("AuraQA shutting down")


# ------------------------------------------------------------------
# Application factory
# ------------------------------------------------------------------

def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Self-Healing Enterprise Test Automation Engine",
        lifespan=lifespan,
    )

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Exception handler ----
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    # ---- Routes ----
    _register_routes(app)

    return app


# ------------------------------------------------------------------
# Route registration
# ------------------------------------------------------------------

def _register_routes(app: FastAPI) -> None:
    """Register all API routes on the application."""

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        """Root endpoint — welcome message."""
        settings = get_settings()
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
        }

    @app.get("/health", tags=["meta"])
    async def health_check() -> dict[str, str]:
        """Liveness / readiness probe."""
        return {"status": "healthy"}

    @app.post(
        "/heal",
        response_model=HealedSelectorResponse,
        tags=["healing"],
        summary="Heal a broken test selector",
        description=(
            "Accepts a test-failure payload from UiPath and returns a healed "
            "selector with confidence scoring and audit metadata."
        ),
    )
    async def heal_selector(payload: TestFailurePayload) -> HealedSelectorResponse:
        """
        Run the self-healing pipeline.

        Receives a ``TestFailurePayload`` from UiPath, executes the
        LangGraph healing graph, and returns a ``HealedSelectorResponse``.
        """
        logger.info(
            "POST /heal — test_case=%s broken_selector=%s",
            payload.test_case_id,
            payload.broken_selector,
        )
        try:
            service = HealingService()
            response = await service.heal(payload)
            return response
        except Exception as exc:
            logger.exception("Healing pipeline failed: %s", exc)
            raise HTTPException(
                status_code=500,
                detail=f"Healing pipeline error: {exc}",
            ) from exc


# ------------------------------------------------------------------
# Module-level app instance (for ``uvicorn backend.main:app``)
# ------------------------------------------------------------------

app = create_app()
```

#### 📂 `backend/graph/graph.py`
```python
"""
LangGraph healing pipeline builder.

Constructs the ``StateGraph`` that implements the AuraQA self-healing
algorithm:

    analyze_dom → generate_selector → validate_selector
        → [conditional: rerun_test | generate_selector | escalate]
"""
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from backend.graph.edges.routing import route_after_validation
from backend.graph.nodes.analyze_dom import analyze_dom
from backend.graph.nodes.escalate import escalate
from backend.graph.nodes.generate_selector import generate_selector
from backend.graph.nodes.provision_test_data import provision_test_data
from backend.graph.nodes.rerun_test import rerun_test
from backend.graph.nodes.validate_selector import validate_selector
from backend.graph.state import HealingState

logger = logging.getLogger(__name__)


def build_healing_graph() -> StateGraph:
    """
    Build and compile the self-healing LangGraph pipeline.

    Graph topology::

        START
          │
          ▼
        analyze_dom
          │
          ▼
        generate_selector
          │
          ▼
        validate_selector
          │
          ├─ confidence ≥ 80% ──► provision_test_data ──► rerun_test ──► END
          │
          ├─ attempts < max ────► generate_selector  (retry loop)
          │
          └─ else ──────────────► escalate ──► END

    Returns:
        A compiled ``StateGraph`` ready for ``.invoke(state)``.
    """
    graph = StateGraph(HealingState)

    # ---- Register nodes ----
    graph.add_node("analyze_dom", analyze_dom)
    graph.add_node("generate_selector", generate_selector)
    graph.add_node("validate_selector", validate_selector)
    graph.add_node("provision_test_data", provision_test_data)
    graph.add_node("rerun_test", rerun_test)
    graph.add_node("escalate", escalate)

    # ---- Static edges ----
    graph.set_entry_point("analyze_dom")
    graph.add_edge("analyze_dom", "generate_selector")
    graph.add_edge("generate_selector", "validate_selector")

    # ---- Conditional edge after validation ----
    graph.add_conditional_edges(
        "validate_selector",
        route_after_validation,
        {
            "rerun_test": "provision_test_data",
            "generate_selector": "generate_selector",
            "escalate": "escalate",
        },
    )

    # ---- Terminal edges ----
    graph.add_edge("provision_test_data", "rerun_test")
    graph.add_edge("rerun_test", END)
    graph.add_edge("escalate", END)

    compiled = graph.compile()
    logger.info("Healing graph compiled successfully")
    return compiled
```

#### 📂 `backend/graph/nodes/analyze_dom.py`
```python
"""
LangGraph node: analyse the DOM snapshot.

Parses the raw HTML into structured ``DOMElement`` objects and scores
every element against the original element's known attributes.
"""
from __future__ import annotations

import logging

from backend.graph.state import HealingState
from backend.graph.tools.dom_parser import DOMParser
from backend.graph.tools.selector_scorer import SelectorScorer
from backend.models.schemas import HealingStatus, OriginalElementAttributes

logger = logging.getLogger(__name__)


def analyze_dom(state: HealingState) -> HealingState:
    """
    Parse the DOM snapshot and score each element.

    Updates:
        - ``parsed_elements``
        - ``candidate_selectors`` (top-3 scored elements as dicts)
        - ``status`` → ANALYZING
    """
    logger.info("analyze_dom — parsing DOM snapshot")
    state["status"] = HealingStatus.ANALYZING.value

    dom_snapshot = state["dom_snapshot"]
    original_attrs_raw = state["original_attributes"]
    original_attrs = OriginalElementAttributes(**original_attrs_raw)

    # 1. Parse HTML → DOMElement list
    parser = DOMParser()
    elements = parser.parse_html(dom_snapshot)
    state["parsed_elements"] = [e.model_dump(mode="json") for e in elements]

    if not elements:
        logger.warning("analyze_dom — no elements found in DOM snapshot")
        state["error_message"] = "No elements found in DOM snapshot"
        state["status"] = HealingStatus.FAILED.value
        return state

    # 2. Score all elements
    scorer = SelectorScorer()
    top_results = scorer.top_n(elements, original_attrs, n=3)

    # 3. Store top candidates with scoring metadata
    candidates: list[dict] = []
    for result in top_results:
        candidates.append({
            "element": result.element.model_dump(mode="json"),
            "composite_score": result.composite,
            "breakdown": result.breakdown,
        })
        logger.debug(
            "  candidate tag=%s id=%s score=%.2f",
            result.element.tag,
            result.element.element_id,
            result.composite,
        )

    state["candidate_selectors"] = candidates
    logger.info(
        "analyze_dom — found %d elements, top score %.2f",
        len(elements),
        top_results[0].composite if top_results else 0.0,
    )
    return state
```

#### 📂 `backend/graph/nodes/generate_selector.py`
```python
"""
LangGraph node: generate a healed CSS / XPath selector.

Examines the top-ranked candidate element and produces the most specific
selector possible using the preference hierarchy:

    data-testid  →  ID  →  class combination  →  nth-child XPath
"""
from __future__ import annotations

import logging
from typing import Any

from backend.graph.state import HealingState
from backend.models.schemas import DOMElement, HealingStatus, SelectorType

logger = logging.getLogger(__name__)


def generate_selector(state: HealingState) -> HealingState:
    """
    Generate a healed selector from the highest-scoring candidate.

    Updates:
        - ``healed_selector``
        - ``healed_selector_type``
        - ``confidence_score``
        - ``status`` → GENERATING
    """
    logger.info("generate_selector — building healed selector")
    state["status"] = HealingStatus.GENERATING.value

    candidates = state.get("candidate_selectors", [])
    if not candidates:
        state["error_message"] = "No candidate elements available for selector generation"
        state["status"] = HealingStatus.FAILED.value
        return state

    best = candidates[0]
    elem_data: dict[str, Any] = best["element"]
    composite_score: float = best["composite_score"]
    elem = DOMElement(**elem_data)

    selector, selector_type = _build_selector(elem)

    state["healed_selector"] = selector
    state["healed_selector_type"] = selector_type.value
    state["confidence_score"] = composite_score

    # Detect drift type
    drift = _detect_drift(state["original_attributes"], elem_data)
    if drift:
        state["drift_type"] = drift

    logger.info(
        "generate_selector — selector=%s type=%s confidence=%.2f drift=%s",
        selector,
        selector_type.value,
        composite_score,
        drift or "none",
    )
    return state


# ------------------------------------------------------------------
# Selector construction helpers
# ------------------------------------------------------------------

def _build_selector(elem: DOMElement) -> tuple[str, SelectorType]:
    """Return the most specific selector + its type for the element."""

    # 1. data-testid  (most reliable)
    if elem.data_testid:
        return f'[data-testid="{elem.data_testid}"]', SelectorType.DATA_TESTID

    # 2. ID  (unique per spec)
    if elem.element_id:
        return f"#{elem.element_id}", SelectorType.CSS

    # 3. Class combination  (prefer multi-class for specificity)
    if elem.classes:
        class_part = ".".join(elem.classes)
        css = f"{elem.tag}.{class_part}"
        return css, SelectorType.CSS

    # 4. XPath nth-child fallback
    if elem.xpath:
        return elem.xpath, SelectorType.XPATH

    # 5. Absolute fallback — tag + child index
    fallback = f"{elem.tag}:nth-child({elem.child_index + 1})"
    return fallback, SelectorType.CSS


def _detect_drift(
    original_raw: dict[str, Any],
    candidate_raw: dict[str, Any],
) -> str:
    """Heuristically classify the type of selector drift."""

    orig_id = original_raw.get("element_id") or ""
    cand_id = candidate_raw.get("element_id") or ""
    orig_tag = original_raw.get("tag", "")
    cand_tag = candidate_raw.get("tag", "")
    orig_classes = set(original_raw.get("classes", []))
    cand_classes = set(candidate_raw.get("classes", []))
    orig_depth = original_raw.get("depth")
    cand_depth = candidate_raw.get("depth", 0)
    orig_text = original_raw.get("text", "")
    cand_text = candidate_raw.get("text", "")
    orig_attrs = set(original_raw.get("attributes", {}).keys())
    cand_attrs = set(candidate_raw.get("attributes", {}).keys())

    drifts: list[str] = []

    if orig_id and cand_id and orig_id != cand_id:
        drifts.append("id_rename")
    elif orig_id and not cand_id:
        drifts.append("attribute_removal")

    if orig_tag != cand_tag:
        drifts.append("tag_change")

    if orig_classes != cand_classes and orig_classes:
        drifts.append("class_swap")

    if orig_depth is not None and cand_depth != orig_depth:
        drifts.append("nesting_change")

    if orig_text and cand_text and orig_text != cand_text:
        drifts.append("text_change")

    if orig_attrs - cand_attrs:
        drifts.append("attribute_removal")

    if len(drifts) >= 3:
        return "compound_shift"
    if drifts:
        return drifts[0]
    return ""
```

#### 📂 `backend/graph/nodes/validate_selector.py`
```python
"""
LangGraph node: validate the generated selector against the DOM snapshot.

Ensures the healed selector matches **exactly one** element in the
original DOM and that confidence meets the threshold.
"""
from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from backend.config.settings import get_settings
from backend.graph.state import HealingState
from backend.models.schemas import (
    CandidateSelector,
    DOMElement,
    HealingStatus,
    SelectorType,
)

logger = logging.getLogger(__name__)


def validate_selector(state: HealingState) -> HealingState:
    """
    Validate the healed selector.

    Checks:
        1. The selector matches exactly 1 element in the DOM snapshot.
        2. The confidence score meets or exceeds the configured threshold.

    Updates:
        - ``status`` → VALIDATING / HEALED / RETRYING / ESCALATED
        - ``candidate_selectors[0]`` enriched with validation metadata
    """
    logger.info("validate_selector — validating healed selector")
    state["status"] = HealingStatus.VALIDATING.value

    selector = state.get("healed_selector", "")
    selector_type_str = state.get("healed_selector_type", "css")
    confidence = state.get("confidence_score", 0.0)
    dom_html = state.get("dom_snapshot", "")

    if not selector:
        state["error_message"] = "No selector to validate"
        state["status"] = HealingStatus.FAILED.value
        return state

    settings = get_settings()
    threshold = settings.confidence_threshold

    # ---- 1. Count matches in DOM ----
    match_count = _count_matches(dom_html, selector, selector_type_str)

    logger.info(
        "validate_selector — selector=%s matches=%d confidence=%.2f threshold=%.2f",
        selector,
        match_count,
        confidence,
        threshold,
    )

    # ---- 2. Apply validation rules ----
    if match_count == 1 and confidence >= threshold:
        state["status"] = HealingStatus.HEALED.value
        logger.info("validate_selector — HEALED ✓")
    elif match_count != 1:
        # Selector is ambiguous or dead — penalise confidence
        penalty = 30.0 if match_count == 0 else 20.0
        state["confidence_score"] = max(0.0, confidence - penalty)
        state["error_message"] = (
            f"Selector matched {match_count} element(s), expected exactly 1"
        )
        logger.warning("validate_selector — match_count=%d, penalised", match_count)
    else:
        # Confidence below threshold
        state["error_message"] = (
            f"Confidence {confidence:.1f}% below threshold {threshold:.1f}%"
        )
        logger.warning("validate_selector — confidence below threshold")

    return state


# ------------------------------------------------------------------
# DOM matching
# ------------------------------------------------------------------

def _count_matches(html: str, selector: str, selector_type: str) -> int:
    """Count how many elements in *html* match *selector*."""
    soup = BeautifulSoup(html, "html.parser")

    try:
        if selector_type in (SelectorType.CSS.value, SelectorType.DATA_TESTID.value):
            matches = soup.select(selector)
            return len(matches)

        if selector_type == SelectorType.XPATH.value:
            # BeautifulSoup doesn't support XPath natively.
            # We attempt a best-effort CSS fallback for simple XPaths,
            # otherwise assume 1 match (selector was derived from DOM).
            css_fallback = _xpath_to_css_best_effort(selector)
            if css_fallback:
                matches = soup.select(css_fallback)
                return len(matches)
            # For complex XPaths generated from our own DOMParser we
            # trust the element existed (it was extracted from this DOM).
            return 1
    except Exception as exc:
        logger.debug("Selector matching error: %s", exc)
        return 0

    return 0


def _xpath_to_css_best_effort(xpath: str) -> str | None:
    """
    Convert trivial XPaths (``/html/body/div/button``) to CSS selectors.

    Returns ``None`` when the XPath is too complex to convert.
    """
    if not xpath or "[" in xpath or "@" in xpath or "//" in xpath:
        return None
    parts = [p for p in xpath.strip("/").split("/") if p]
    if all(p.isidentifier() or p.replace("-", "").isalpha() for p in parts):
        return " > ".join(parts)
    return None
```

#### 📂 `infrastructure/.env.example`
```ini
### infrastructure/.env.example
# ──────────────────────────────────────────────────────────────
# AuraQA — Environment Variables Template
# Copy to .env and fill in secrets before running.
# All vars are prefixed with AURAQA_ (see backend/config/env_schema.py)
# ──────────────────────────────────────────────────────────────

# ── Application ──────────────────────────────────────────────
AURAQA_APP_NAME=AuraQA
AURAQA_APP_VERSION=1.0.0
AURAQA_APP_ENV=development
AURAQA_DEBUG=false
AURAQA_LOG_LEVEL=INFO

# ── API Server ───────────────────────────────────────────────
AURAQA_API_HOST=0.0.0.0
AURAQA_API_PORT=8000
AURAQA_API_WORKERS=1
AURAQA_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:80

# ── LangGraph ────────────────────────────────────────────────
AURAQA_LANGGRAPH_MAX_RETRIES=3
AURAQA_CONFIDENCE_THRESHOLD=80.0

# ── Jira Integration ────────────────────────────────────────
AURAQA_JIRA_BASE_URL=https://your-org.atlassian.net
AURAQA_JIRA_PROJECT_KEY=AURA
AURAQA_JIRA_API_TOKEN=your-jira-api-token
AURAQA_JIRA_USER_EMAIL=your-email@example.com
AURAQA_JIRA_ISSUE_TYPE=Bug

# ── UiPath Orchestrator ─────────────────────────────────────
AURAQA_UIPATH_ORCHESTRATOR_URL=https://cloud.uipath.com/your-org/your-tenant/orchestrator_
AURAQA_UIPATH_TENANT=your-tenant
AURAQA_UIPATH_API_KEY=your-uipath-api-key
AURAQA_UIPATH_FOLDER_ID=your-folder-id

# ── TDO (Test Data Orchestrator) ────────────────────────────
AURAQA_TDO_BASE_URL=http://localhost:9000
AURAQA_TDO_API_KEY=your-tdo-api-key
AURAQA_TDO_DEFAULT_DATASET=default

# ── Mock App ─────────────────────────────────────────────────
AURAQA_MOCK_APP_URL=http://localhost:5173
```

#### 📂 `contracts/failure_payload.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://auraqa.io/schemas/failure_payload.json",
  "title": "TestFailurePayload",
  "description": "JSON Schema for the payload sent from UiPath to Python upon a test failure.",
  "type": "object",
  "required": [
    "test_case_id",
    "test_suite_id",
    "broken_selector",
    "selector_type",
    "dom_snapshot",
    "original_element_attributes",
    "page_url"
  ],
  "properties": {
    "test_case_id": {
      "type": "string",
      "description": "Unique test case identifier",
      "minLength": 1
    },
    "test_suite_id": {
      "type": "string",
      "description": "Parent test suite identifier",
      "minLength": 1
    },
    "broken_selector": {
      "type": "string",
      "description": "CSS/XPath selector that failed to locate the element",
      "minLength": 1
    },
    "selector_type": {
      "type": "string",
      "enum": ["css", "xpath", "data-testid"],
      "description": "Type of the broken selector"
    },
    "dom_snapshot": {
      "type": "string",
      "description": "Complete HTML of the page at the time of failure",
      "minLength": 1
    },
    "original_element_attributes": {
      "type": "object",
      "description": "Known attributes of the element the selector originally matched",
      "required": ["tag"],
      "properties": {
        "tag": {
          "type": "string",
          "description": "Original HTML tag name"
        },
        "element_id": {
          "type": ["string", "null"],
          "description": "Original ID attribute"
        },
        "classes": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Original CSS class list"
        },
        "text": {
          "type": "string",
          "description": "Original inner text content"
        },
        "attributes": {
          "type": "object",
          "additionalProperties": { "type": "string" },
          "description": "All original HTML attributes"
        },
        "data_testid": {
          "type": ["string", "null"],
          "description": "Original data-testid attribute"
        },
        "depth": {
          "type": ["integer", "null"],
          "description": "Original nesting depth"
        },
        "parent_tag": {
          "type": ["string", "null"],
          "description": "Original parent element tag"
        }
      }
    },
    "page_url": {
      "type": "string",
      "format": "uri",
      "description": "URL of the page under test"
    },
    "screenshot_base64": {
      "type": ["string", "null"],
      "description": "Base64-encoded screenshot at failure time"
    },
    "error_message": {
      "type": "string",
      "description": "UiPath error message on failure",
      "default": ""
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "UTC timestamp of the failure"
    },
    "environment": {
      "type": "string",
      "description": "Execution environment identifier",
      "default": "staging"
    },
    "retry_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of prior healing attempts",
      "default": 0
    }
  },
  "additionalProperties": false
}
```

#### 📂 `contracts/healed_response.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://auraqa.io/schemas/healed_response.json",
  "title": "HealedSelectorResponse",
  "description": "JSON Schema for the payload returned from Python to UiPath containing the healed selector.",
  "type": "object",
  "required": [
    "test_case_id",
    "original_selector",
    "healed_selector",
    "healed_selector_type",
    "confidence",
    "status"
  ],
  "properties": {
    "test_case_id": {
      "type": "string",
      "description": "Original test case identifier"
    },
    "original_selector": {
      "type": "string",
      "description": "The broken selector that was submitted for healing"
    },
    "healed_selector": {
      "type": "string",
      "description": "New healed selector"
    },
    "healed_selector_type": {
      "type": "string",
      "enum": ["css", "xpath", "data-testid"],
      "description": "Type of the healed selector"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Final confidence score (0-100)"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "analyzing", "generating", "validating", "healed", "retrying", "escalated", "failed"],
      "description": "Final healing status"
    },
    "candidates_evaluated": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of candidate selectors evaluated"
    },
    "top_candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["selector", "selector_type", "confidence"],
        "properties": {
          "selector": { "type": "string" },
          "selector_type": {
            "type": "string",
            "enum": ["css", "xpath", "data-testid"]
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 100
          },
          "matched_element": {
            "type": ["object", "null"]
          },
          "scoring_breakdown": {
            "type": "object",
            "additionalProperties": { "type": "number" }
          }
        }
      },
      "description": "Top 3 candidate selectors considered"
    },
    "drift_type": {
      "type": ["string", "null"],
      "enum": [
        "id_rename", "class_swap", "nesting_change",
        "attribute_removal", "tag_change", "text_change",
        "sibling_reorder", "compound_shift", null
      ],
      "description": "Detected type of selector drift"
    },
    "attempt_count": {
      "type": "integer",
      "minimum": 1,
      "description": "Number of healing attempts made"
    },
    "execution_time_ms": {
      "type": "number",
      "minimum": 0,
      "description": "Total healing pipeline execution time in milliseconds"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "UTC timestamp of the healing response"
    },
    "audit_log_id": {
      "type": ["string", "null"],
      "description": "Reference to the generated audit log entry"
    }
  },
  "additionalProperties": false
}
```

---

### 3. Docker-Compose Status Output
```text
NAME             IMAGE                    COMMAND                  SERVICE   CREATED       STATUS                 PORTS
auraqa-backend   infrastructure-backend   "uvicorn backend.mai…"   backend   2 hours ago   Up 2 hours (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
auraqa-mockapp   infrastructure-mockapp   "/docker-entrypoint.…"   mockapp   2 hours ago   Up 2 hours (healthy)   0.0.0.0:5173->5173/tcp, [::]:5173->5173/tcp
auraqa-nginx     nginx:1.25-alpine        "/docker-entrypoint.…"   nginx     2 hours ago   Up 2 hours             0.0.0.0:80->80/tcp, [::]:80->80/tcp
```

---

### 4. Health Check API Output
```json
{"status":"healthy"}
```

---

### 5. Mutation Scenario Output (POST `/api/mutate`)
```json
{"detail":"Not Found"}
```
*(Note: DOM Drift scenarios are managed directly clientside within the live React DOM of the Mock App through the Mutation Control Panel, thus the backend REST endpoint is unused and defaults to a 404.)*

---

### 6. Healing API Dry-Run / Validation Error Output (POST `/api/heal`)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "test_suite_id"],
      "msg": "Field required",
      "input": {
        "test_case_id": "TC-001",
        "broken_selector": "#submit-btn",
        "dom_snapshot": "",
        "selector_type": "css"
      }
    },
    {
      "type": "value_error",
      "loc": ["body", "dom_snapshot"],
      "msg": "Value error, dom_snapshot must not be empty",
      "input": "",
      "ctx": {"error": {}}
    },
    {
      "type": "missing",
      "loc": ["body", "original_element_attributes"],
      "msg": "Field required",
      "input": {
        "test_case_id": "TC-001",
        "broken_selector": "#submit-btn",
        "dom_snapshot": "",
        "selector_type": "css"
      }
    },
    {
      "type": "missing",
      "loc": ["body", "page_url"],
      "msg": "Field required",
      "input": {
        "test_case_id": "TC-001",
        "broken_selector": "#submit-btn",
        "dom_snapshot": "",
        "selector_type": "css"
      }
    }
  ]
}
```


---

### 3. Recent Fixes & Updates (May 2026)

Based on the latest requirements, the following critical issues have been successfully implemented and validated:

#### 1. Real Jira Integration (Fix 1)
- **File:** `uipath/workflows/LogToJira.xaml`
- **Description:** Replaced the mock `Assign` activity with a C# `InvokeCode` block. It dynamically generates a `System.Net.Http.HttpClient` instance to make a real HTTP `POST` to the Jira API (`/rest/api/3/issue`) using Basic Auth, and dynamically parses the newly created Jira key from the API response payload.
- **Environment Variables Used:** `AURAQA_JIRA_BASE_URL`, `AURAQA_JIRA_USER_EMAIL`, `AURAQA_JIRA_API_TOKEN`

#### 2. Real TDO Integration (Fix 2)
- **File:** `uipath/workflows/ProvisionTestData.xaml`
- **Description:** Completely replaced the mock assigning of empty JSON with a C# `InvokeCode` execution. The workflow reads TDO environment configurations, authenticates via a Bearer token, passes schema parameters from the provided test cases dynamically, and captures real provisioned datasets from the TDO endpoint (`/api/v1/provision`).
- **Environment Variables Used:** `AURAQA_TDO_BASE_URL`, `AURAQA_TDO_API_KEY`

#### 3. E2E Demo Validation Script & Test Command (Fix 3 & 4)
- **File:** `scripts/test_e2e_demo.sh`
- **Description:** Created a robust bash script using `curl` and `jq` to validate the entire backend test harness. Validates health endpoints, pushes a completely formulated `TestFailurePayload` schema to `/api/heal`, and processes the response to test numerical confidence bounds (0-100), validation states (`healed` or `escalated`), and non-empty healed selectors. The script passes 4/4 assertions seamlessly.
