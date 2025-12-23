library(shiny)
library(deSolve)
library(ggplot2)
library(tidyr)

# -----------------------------------------------------------------------------
# 典型用途：复杂数学模型模拟 (Mathematical Modeling)
# 核心特色：
# 1. R 语言在统计和数学建模领域的统治力
# 2. 实时求解微分方程 (ODE) 并可视化
# 3. 适合流行病学、生态学、药代动力学等领域的仿真工具
# -----------------------------------------------------------------------------

# SEIR 模型定义 (Susceptible-Exposed-Infected-Recovered)
seir_model <- function(time, state, parameters) {
  with(as.list(c(state, parameters)), {
    dS <- -beta * S * I / N
    dE <- beta * S * I / N - sigma * E
    dI <- sigma * E - gamma * I
    dR <- gamma * I
    return(list(c(dS, dE, dI, dR)))
  })
}

ui <- fluidPage(
  theme = bslib::bs_theme(bootswatch = "flatly"),
  
  titlePanel("🦠 传染病动力学模型 (SEIR) 仿真"),
  
  sidebarLayout(
    sidebarPanel(
      h4("模型参数"),
      sliderInput("R0", "基本传染数 (R0):", min = 0.5, max = 10, value = 3.0, step = 0.1),
      sliderInput("incubation", "潜伏期 (1/sigma, 天):", min = 1, max = 14, value = 5),
      sliderInput("infectious", "传染期 (1/gamma, 天):", min = 1, max = 21, value = 7),
      hr(),
      numericInput("N", "总人口 (N):", value = 1000000),
      sliderInput("days", "模拟天数:", min = 30, max = 365, value = 100),
      
      helpText("SEIR 模型包含：易感者(S)、暴露者(E)、感染者(I)、康复者(R)")
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel("曲线图", plotOutput("seir_plot")),
        tabPanel("数据表", tableOutput("seir_table")),
        tabPanel("模型说明", 
                 withMathJax(),
                 h3("微分方程组"),
                 p("$$\\frac{dS}{dt} = -\\beta \\frac{SI}{N}$$"),
                 p("$$\\frac{dE}{dt} = \\beta \\frac{SI}{N} - \\sigma E$$"),
                 p("$$\\frac{dI}{dt} = \\sigma E - \\gamma I$$"),
                 p("$$\\frac{dR}{dt} = \\gamma I$$")
        )
      )
    )
  )
)

server <- function(input, output) {
  
  # 响应式求解 ODE
  sim_data <- reactive({
    # 参数转换
    gamma <- 1 / input$infectious
    sigma <- 1 / input$incubation
    beta <- input$R0 * gamma
    
    parms <- c(beta = beta, sigma = sigma, gamma = gamma, N = input$N)
    init <- c(S = input$N - 1, E = 0, I = 1, R = 0)
    times <- seq(0, input$days, by = 1)
    
    out <- ode(y = init, times = times, func = seir_model, parms = parms)
    as.data.frame(out)
  })
  
  output$seir_plot <- renderPlot({
    data <- sim_data()
    # 转换为长格式以便 ggplot 绘图
    data_long <- pivot_longer(data, cols = c(S, E, I, R), names_to = "State", values_to = "Count")
    
    ggplot(data_long, aes(x = time, y = Count, color = State)) +
      geom_line(size = 1.2) +
      scale_color_manual(values = c("S"="#3498db", "E"="#f1c40f", "I"="#e74c3c", "R"="#2ecc71")) +
      theme_minimal() +
      labs(title = paste0("疫情发展预测 (R0 = ", input$R0, ")"),
           x = "天数", y = "人数") +
      theme(legend.position = "top", text = element_text(size = 14))
  })
  
  output$seir_table <- renderTable({
    head(sim_data(), 20)
  })
}

shinyApp(ui = ui, server = server)
