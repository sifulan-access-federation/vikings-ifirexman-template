{{/*
Expand the name of the chart.
*/}}
{{- define "vikings.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "vikings.fullname" -}}
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
{{- define "vikings.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "vikings.labels" -}}
helm.sh/chart: {{ include "vikings.chart" . }}
{{ include "vikings.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "vikings.selectorLabels" -}}
app.kubernetes.io/name: {{ include "vikings.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "vikings.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "vikings.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
site-config.conf template
*/}}
{{- define "vikings.site-config-conf" -}}
<VirtualHost *:80>
  ServerName https://{{ .Values.vikings.domain }}:443
  UseCanonicalName On
  ServerAdmin {{ .Values.vikings.support }}
  DocumentRoot /vikings
  WSGIScriptAlias / /vikings/vikings/wsgi.py
  WSGIDaemonProcess {{ .Values.vikings.domain }} python-path=/vikings
  WSGIProcessGroup {{ .Values.vikings.domain }}
  
  <Directory /vikings/vikings>
    <Files wsgi.py>
      Require all granted
    </Files>
  </Directory>

  Alias /static /static
  <Directory /static>
    Require all granted
  </Directory>
  
  ErrorLog /vikings/logs/apache.error.log
  CustomLog /vikings/logs/apache.access.log combined
</VirtualHost>
{{- end }}

{{/*
main.css template
*/}}
{{- define "vikings.main-css" -}}
:root {
  --brand-primary: {{ .Values.vikings.colour.hex.primary }};
  --brand-neutral: {{ .Values.vikings.colour.hex.neutral }};
  --brand-dark: {{ .Values.vikings.colour.hex.dark }};
  --brand-light: {{ .Values.vikings.colour.hex.light }};
  --brand-primary-rgba: {{ .Values.vikings.colour.rgba.primary }};
  --brand-neutral-rgba: {{ .Values.vikings.colour.rgba.neutral }}; /* Stroke colour needs to be updated manually in .navbar-toggler-colour .navbar-toggler-icon */
  --brand-dark-rgba: {{ .Values.vikings.colour.rgba.dark }};
  --brand-light-rgba: {{ .Values.vikings.colour.rgba.light }};
}

/* Tags */
html, body {
  height: 100%;
  width: 100%;
  background-color: var(--brand-primary);
  color: #000000;
  margin-top: 2.5rem;
  font-weight: normal;
  font-family: "Poppins", "Segoe UI" , "Segoe" , "SegoeUI-Regular-final", Tahoma, Helvetica, Arial, sans-serif;
  -ms-overflow-style: -ms-autohiding-scrollbar;
}

h1, h2, h3, h4, h5, h6 {
  color: #444444;
  font-family: "Poppins", sans-serif;
}

ul {
  margin: 0;
}

pre {
  font-family: "Courier New", monospace;
  color: var(--brand-primary);
  font-size: 4px;
  font-weight: bold;
  position: absolute;
  top: 10px;
}

code {
  font-family: "Roboto Mono", monospace;
  color: var(--brand-primary);
  font-weight: bold;
}

a {
  color: var(--brand-dark);
}

a:hover {
  color: var(--brand-neutral);
  text-decoration: none;
}

a:active {
  color: var(--brand-light);
}

/* Placeholders */
/* ::-webkit-input-placeholder {
  color:#c9d7ed !important;
}

::-moz-placeholder {
  color:#c9d7ed !important;
}

::-ms-placeholder {
  color:#c9d7ed !important;
}

::placeholder {
  color:#c9d7ed !important;
} */

/* Pretty Base Components */
#brandingWrapper {
  background-color: var(--brand-primary);
}

#fullPage, #brandingWrapper {
  width: 100%;
  height: 100%;
  background-color: inherit;
}

#contentWrapper {
  position: relative;
  width: 500px;
  height: 100%;
  overflow: auto;
  margin-left: -500px;
  margin-right: 0px;
}

#branding {
  height: 100%;
  margin-right: 500px;
  margin-left: 0px;
  background-color: inherit;
  background-repeat: no-repeat;
  background-size: cover;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
}

#content {
  min-height: 100%;
  height: auto !important;
  /**margin: 0 auto -55px auto;**/
  margin: auto;
  padding: 100px 80px 0px 80px;
}

/* Essential Components */
.backgroundImage {
  background-image: url(/static/core/img/background.jpg);
}

.logo {
  height: auto;
  width: auto;
  max-height: 55px;
}

.content-section {
  background: #e9ecef;
  padding: 20px 40px;
  border: 1px solid #dddddd;
  border-radius: 8px;
  /*margin-top: 10px;*/
  margin-bottom: 20px;
  box-shadow: rgba(0,0,0,0.15) 0px 15px 25px, rgba(0,0,0,0.05) 0px 5px 10px;
}

.alert {
  border-radius: 8px;
  box-shadow: rgba(0,0,0,0.15) 0px 15px 25px, rgba(0,0,0,0.05) 0px 5px 10px;
}

.body {
  font-size: 0.9em;
}

/* Alignment */
.center {
  text-align: center;
  margin: auto;
  display: inline-block;
}

.float {
  float: left;
}

.main {
  margin-left: 140px; /* Same width as the sidebar + left position in px */
  padding: 0px 10px;
}

@media screen and (max-height: 450px) {
  .sidenav {padding-top: 15px;}
  .sidenav a {font-size: 18px;}
}

#HASH {
  display: flex;
  justify-content: space-between;
}

/* Pagination */
.pagination-container {
  padding: 20px 40px;
}

/* Search bar */
.wrapper {
  position: relative;
  display: flex;
  min-height: 38.8px;
  min-width: 100px;
}

.search-bar {
  background: #CBCED2;
  border: 1px solid #CFD4DA;
  border-radius: 10px;
  padding-left: 30px;
  color: #333333;
  outline: 0;
}

.search-bar:focus {
  border: 0;
  box-shadow: 0 0 2pt 1pt var(--brand-primary);
}

.search-icon {
  font-size: 13px;
  position: absolute;
  top: 12px;
  left: 8px;
  width: 14px;
}

.clear-icon {
  position: absolute;
  top: 13px;
  right: 12px;
  width: 10px;
  cursor: pointer;
  visibility: hidden;
}

/* Navbar */
.bg-navbar {
  background-color: #ffffff;
}

.site-header .navbar-nav .nav-link {
  font-weight: 600;
  color: var(--brand-dark);
}

.site-header .navbar-nav .nav-link:hover {
  color: var(--brand-neutral);
}

.site-header .navbar-nav .nav-link:active {
  color: var(--brand-light);
}

.navbar-toggler-colour .navbar-toggler-icon {
  background-image: url("data:image/svg+xml;charset=utf8,%3Csvg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath stroke='{{ .Values.vikings.colour.rgba.neutral }}' stroke-width='2' stroke-linecap='round' stroke-miterlimit='10' d='M4 8h24M4 16h24M4 24h24'/%3E%3C/svg%3E");
}

.navbar-toggler-colour.navbar-toggler {
  border-color: var(--brand-neutral);
}

/* Sidenav */
.sidenav {
  background: #e9ecef;
  padding: 8px;
  border: 1px solid #dddddd;
  border-radius: 8px;
  /*margin-top: 10px;*/
  margin-bottom: 20px;
  word-wrap: break-word;
  box-shadow: rgba(0,0,0,0.15) 0px 15px 25px, rgba(0,0,0,0.05) 0px 5px 10px;
}

.sidenav a {
  padding: 6px 16px 6px 16px;
  text-decoration: none;
  font-size: 18px;
  color: var(--brand-dark);
  display: block;
}

.sidenav a:hover {
  color: var(--brand-neutral);
}

.sidenav a:active {
  color: var(--brand-light);
}

/* Buttons */
.btn {
  font-size: 14px;
}

.btn-info {
  color: #ffffff;
  background-color: var(--brand-dark);
  border-color: var(--brand-dark);
}

.btn-info:hover {
  background-color: var(--brand-neutral);
  border-color: var(--brand-neutral);
}

.btn-info:not(:disabled):not(.disabled).active:focus,.btn-info:not(:disabled):not(.disabled):active:focus,.show>.btn-info.dropdown-toggle:focus{
  background-color: var(--brand-light);
  border-color: var(--brand-light);
  box-shadow:0 0 0 .2rem var(--brand-light-rgba)
}

.btn-info.disabled, .btn-info:disabled {
  background-color: var(--brand-neutral);
  border-color: var(--brand-neutral);
}

.btn-outline-info {
  color: var(--brand-neutral);
  background-color: #e9ecef;
  background-image: none;
  border-color: var(--brand-neutral);
}

.btn-outline-info:hover {
  color: #ffffff;
  background-color: var(--brand-neutral);
  border-color: var(--brand-neutral);
}

.btn-outline-info:focus {
  background-color: var(--brand-neutral);
  border-color: var(--brand-neutral);
  box-shadow:0 0 0 .2rem var(--brand-light-rgba)
}

.btn-outline-info:not(:disabled):not(.disabled).active:focus,.btn-outline-info:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-info.dropdown-toggle:focus {
  background-color: var(--brand-neutral);
  border-color: var(--brand-neutral);
  box-shadow:0 0 0 .2rem var(--brand-light-rgba)
}

/* Button Tooltip */
.btn-tooltip {
  position: relative;
  display: inline-block;
}

.btn-tooltip .tooltiptext {
  visibility: hidden;
  width: 150px;
  background-color: #555;
  color: #ffffff;
  text-align: center;
  border-radius: 6px;
  padding: 5px;
  position: absolute;
  z-index: 99999;
  bottom: 150%;
  left: 50%;
  margin-left: -75px;
  opacity: 0;
  transition: opacity 0.3s;
}

.btn-tooltip .tooltiptext::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #555 transparent transparent transparent;
}

.btn-tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 0.95;
}

/* Button Link */
.btn-link, .btn-link:hover, .btn-link:active {
background: #f25f0f;
border-radius: 7px;
text-decoration: none;
text-transform: uppercase;
border: none;
color: white;
padding: 3px 6px;
text-align: center;
display: inline-block;
font-size: 10px;
}

.btn-link:hover {
  background: #d9550d;
}

.btn-link:active {
  background: #bd4b0d;
}

/* Table */
.list-table {
  border-radius: 5px;
  font-size: 16px;
  font-weight: normal;
  border: none;
  border-collapse: collapse;
  width: 100%;
  max-width: 100%;
  margin-bottom: 1rem;
  white-space: nowrap;
  background-color: white;
}

.list-table td, .list-table th {
  text-align: center;
  padding: 12px;
}

.list-table td {
  /*border-right: 1px solid #f8f8f8;*/
  font-size: 16px;
}

.list-table thead th {
  color: #ffffff;
  background: var(--brand-primary);
}

.list-table tr:nth-child(even) {
  background: #F8F8F8;
}

/* Mobile-responsive Table */
@media (max-width: 767px) {
  .list-table {
      display: block;
      width: 100%;
  }
  /*
  .table-wrapper:before{
      content: "Scroll horizontally >";
      display: block;
      text-align: right;
      font-size: 11px;
      color: white;
      padding: 0 0 10px;
  }
  */
  .list-table thead, .list-table tbody, .list-table thead th {
      display: block;
  }
  .list-table thead th:last-child{
      border-bottom: none;
  }
  .list-table thead {
      float: left;
  }
  .list-table tbody {
      width: auto;
      position: relative;
      overflow-x: auto;
  }
  .list-table td, .list-table th {
      padding: 20px .625em .625em .625em;
      height: 60px;
      vertical-align: middle;
      box-sizing: border-box;
      overflow-x: hidden;
      overflow-y: auto;
      width: 120px;
      font-size: 13px;
      text-overflow: ellipsis;
  }
  .list-table thead th {
      text-align: left;
      border-bottom: 1px solid #E6E4E4;
  }
  .list-table tbody tr {
      display: table-cell;
  }
  .list-table tbody tr:nth-child(odd) {
      background: none;
  }
  .list-table tr:nth-child(even) {
      background: transparent;
  }
  .list-table tr td:nth-child(odd) {
      background: #F8F8F8;
      /*border-right: 1px solid #E6E4E4;*/
  }
  /*
  .list-table tr td:nth-child(even) {
      border-right: 1px solid #E6E4E4;
  }
  */
  .list-table tbody td {
      display: block;
      text-align: center;
  }
}

/* Form Components */
.form-control:focus {
  border-color: var(--brand-primary);
  box-shadow: 0 0 8px var(--brand-light-rgba);
}

.help-text {
  color: #6e757c;
}

.profile-img {
  height: 100px;
  width: 100px;
  margin-right: 20px;
  margin-bottom: 16px;
  box-shadow: rgba(0,0,0,0.15) 0px 15px 25px, rgba(0,0,0,0.05) 0px 5px 10px;
}

.object-header {
  font-weight: bold;
}

/* Addresses issue with crispy-forms not displaying ImageField and FileField errors */
.invalid-feedback {
  display: initial;
}

/* Form File Upload Field */
div span.text-break {
  word-wrap: break-word;
}

div.form-control.d-flex.h-auto {
  border-radius: 0px 10px 10px 0px;
}

span.input-group-text {
  border-radius: 10px;
}

div.form-control.custom-file {
  border-radius: 10px;
}

label.custom-file-label.text-truncate {
  border-radius: 10px;
  /* background-color: #FB7483; */
}

.form-control.d-flex.h-auto {
  background-color: #C0C4C9;
}

.form-control.d-flex.h-auto span a {
  color: #495057;
}

/* Other Form Fields */
#id_confirm_password, #id_display_name, #id_permissions, #id_username, #id_password,
#id_new_password, #id_owner, #id_mac_address, #id_date_registered, #id_nationality,
#id_mobile, #id_location, #id_first_name, #id_last_name, #id_email, #id_personal_unique_id,
#id_name, #id_description {
  border-radius: 10px;
}

#id_confirm_password:disabled, #id_display_name:disabled, #id_permissions:disabled,
#id_username:disabled, #id_password:disabled, #id_new_password:disabled, #id_mobile:disabled,
#id_owner:disabled, #id_mac_address:disabled, #id_date_registered:disabled, #id_nationality:disabled,
#id_location:disabled, #id_first_name:disabled, #id_last_name:disabled, #id_email:disabled,
#id_personal_unique_id:disabled, #id_name:disabled, #id_description:disabled {
  background: #C0C4C9;
}

#id_permissions {
  height: 300px;
}

/* Viewport */
@-ms-viewport { width: device-width; }

@-moz-viewport { width: device-width; }

@-o-viewport { width: device-width; }

@-webkit-viewport { width: device-width; }

@viewport { width: device-width; }

/* Form factor: intermediate layout (WAB in non-snapped view falls in here) */
@media only screen and (max-width: 600px) {
  html, body {
      min-width: 260px;
  }

  #brandingWrapper {
      display: none;
  }

  #contentWrapper {
      float: none;
      width: 100%;
      margin: 0px auto;
  }

  #content {
      width: 400px;
      padding-left: 0px;
      padding-right: 0px;
      margin-left: auto;
      margin-right: auto;
  }
}

@media only screen and (max-width: 450px) {
  body {
      font-size: 0.8em;
  }

  #content {
      width:auto;
      margin-right:33px;
      margin-left:25px;
  }
}

/* Form factor: snapped WAB (for WAB to work in snapped view, the content wrapper width has to be set to 260px) */
@media only screen and (max-width:280px)
{
  #contentWrapper
  {
      width:260px;
  }
}
{{- end }}
