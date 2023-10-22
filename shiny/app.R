#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(shinydashboard)
library(httr)
library(jsonlite)
library(DT)


ui <- dashboardPage(
  dashboardHeader(title = "Applicants"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Applicants Table", tabName = "table", icon = icon("table")),
      menuItem("Start C9", tabName = "startC9", icon = icon("rocket")),
      menuItem("Upload Files", tabName = "uploadFiles", icon = icon("book"))
    )
  ),
  dashboardBody(
    tabItems(
      tabItem(tabName = "table",
              DTOutput("applicantsTable"),
              textInput("userNameInput", "Enter user_name:"),
              actionButton("addUser", "Add User"),
              actionButton("goToStartC9", "Overview and start C9")
      ),
      tabItem(tabName = "startC9",
              h2("User Details:"),
              verbatimTextOutput("selectedUserDetails"),
              br(),
              actionButton("bigButton", "Start C9", style = "font-size: 20px; padding: 20px; color: white; background-color: #007BFF;")
      ),
      tabItem(tabName = "uploadFiles",
              h2("Upload Files"),
              fileInput("file1", "Choose a File",
                        multiple = T,
                        accept = c("text/csv")),
              actionButton("uploadBtn", "Upload to Remote Server"),
              actionButton("startBtn", "Start Test")
      )
    )
  )
)

server <- function(input, output, session) {
  data <- reactiveVal(NULL)
  
  observeEvent(input$uploadBtn, {
    inFile <- input$file1
    if (is.null(inFile)) {
      output$uploadStatus <- renderText({ "No File Uploaded." })
      return(NULL)
    }
    response <- GET("https://httpbin.org/ip")
    ip_info <- content(response, "parsed")
    ip_address <- paste0(ip_info$origin, "/32")
    # Open inbound traffic from my IP
    response <- POST("http://localhost:5000/set_ingress_open", body = list(IpAddress = ip_address), encode = "json")
    if (status_code(response) == 200) {
      response <- GET("http://localhost:5000/get_instace_ip")
      if (status_code(response) == 200) {
        ec2_ip <- fromJSON(content(response, "text"))$Ip
        remote_path <- paste0("ec2-user@",ec2_ip,":/home/ec2-user/environment/.")
        local_path <- inFile$datapath[1]
        result <- system(paste("scp", local_path, remote_path))
        if (result == 0) {
          output$uploadStatus <- renderText({ "File Upload success!" })
        } else {
          output$uploadStatus <- renderText({ "Something scheiße wieder" })
        }
      }
    }
  })
  
  observeEvent(input$startBtn, {
    response <- POST("http://localhost:5000/set_egress")
    if (status_code(response) == 200) {
      output$uploadStatus <- renderText({ "Ingress & Egress updated" })
    }
  })
  
  observe({
    response <- GET("http://localhost:5000/applicants")
    if (status_code(response) == 200) {
      data(fromJSON(content(response, "text"))$Users)
    }
  })
  
  output$applicantsTable <- renderDT({
    datatable(as.data.frame(data()), selection = "single")
  })
  
  observeEvent(input$addUser, {
    newUser <- list(UserName = input$userNameInput)
    response <- POST("http://localhost:5000/applicants", body = list(user_name = input$userNameInput), encode = "json")
    
    if (status_code(response) == 201) {
      response <- GET("http://localhost:5000/applicants")
      if (status_code(response) == 200) {
        data(fromJSON(content(response, "text"))$Users)
      }
    }
  })
  
  observeEvent(input$goToStartC9, {
    if (!is.null(input$applicantsTable_rows_selected)) {
      print(input$applicantsTable_rows_selected)
      updateTabItems(session, "tabs", selected = "startC9")
    }
  })
  
  observeEvent(input$bigButton, {
    if (!is.null(input$applicantsTable_rows_selected) &&
        input$applicantsTable_rows_selected <= nrow(data())) {
      selectedUserArn <- data()[input$applicantsTable_rows_selected, 1, drop = FALSE]
      body_data = list(
        createC9 = list(
          name = "Bewerber-env",
          instanceType = "t2.micro",
          connectionType = "CONNECT_SSH",
          ownerArn = "arn:aws:iam::079042499022:user/aws_cli_robert",
          automaticStopTimeMinutes = 100
        ),
        envMember = list(
          environmentId = "",
          userArn = as.character(selectedUserArn),
          permissions = "read-write"
        )
      )
      print(body_data)
      response <- POST("http://localhost:5000/c9_start", body = body_data, encode = "json")
    }
  })
  
  output$selectedUserDetails <- renderPrint({
    if (!is.null(input$applicantsTable_rows_selected) && 
        input$applicantsTable_rows_selected <= nrow(data())) {
      selectedUser <- data()[input$applicantsTable_rows_selected, , drop = FALSE]
      return(selectedUser)
    } else {
      return(NULL)
    }
  })
}

shinyApp(ui = ui, server = server)
