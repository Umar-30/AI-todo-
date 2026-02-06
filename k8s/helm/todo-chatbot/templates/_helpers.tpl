{{/*
Expand the name of the chart.
*/}}
{{- define "todo-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-chatbot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-chatbot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-chatbot.labels" -}}
helm.sh/chart: {{ include "todo-chatbot.chart" . }}
{{ include "todo-chatbot.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-chatbot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-chatbot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo-chatbot.backendLabels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: backend
app: todo-backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todo-chatbot.backendSelectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app: todo-backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo-chatbot.frontendLabels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: frontend
app: todo-frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todo-chatbot.frontendSelectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app: todo-frontend
{{- end }}

{{/*
Recurring Task Service labels
*/}}
{{- define "todo-chatbot.recurringTaskLabels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: recurring-task
app: recurring-task-service
{{- end }}

{{/*
Recurring Task Service selector labels
*/}}
{{- define "todo-chatbot.recurringTaskSelectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app: recurring-task-service
{{- end }}

{{/*
Realtime Sync Service labels
*/}}
{{- define "todo-chatbot.realtimeSyncLabels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: realtime-sync
app: realtime-sync-service
{{- end }}

{{/*
Realtime Sync Service selector labels
*/}}
{{- define "todo-chatbot.realtimeSyncSelectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app: realtime-sync-service
{{- end }}

{{/*
Reminder Service labels
*/}}
{{- define "todo-chatbot.reminderLabels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: reminder
app: reminder-service
{{- end }}

{{/*
Reminder Service selector labels
*/}}
{{- define "todo-chatbot.reminderSelectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app: reminder-service
{{- end }}

{{/*
Audit Service labels
*/}}
{{- define "todo-chatbot.auditLabels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: audit
app: audit-service
{{- end }}

{{/*
Audit Service selector labels
*/}}
{{- define "todo-chatbot.auditSelectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app: audit-service
{{- end }}
