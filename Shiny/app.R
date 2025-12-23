library(shiny)
library(ggplot2)
library(dplyr)

# 生成示例数据
set.seed(42)
df <- data.frame(
  x = 1:100,
  y = cumsum(rnorm(100))
)

# UI
ui <- fluidPage(
  titlePanel("✨ Shiny for R 交互式应用"),
  
  sidebarLayout(
    sidebarPanel(
      sliderInput("n_points", "数据点数量:", 
                  min = 10, max = 100, value = 50),
      selectInput("plot_type", "图表类型:",
                  choices = c("折线图", "散点图", "柱状图"))
    ),
    
    mainPanel(
      plotOutput("main_plot"),
      tableOutput("data_table")
    )
  )
)

# Server
server <- function(input, output) {
  
  output$main_plot <- renderPlot({
    plot_df <- df %>% head(input$n_points)
    
    p <- ggplot(plot_df, aes(x = x, y = y))
    
    if (input$plot_type == "折线图") {
      p <- p + geom_line(color = "#00D9FF")
    } else if (input$plot_type == "散点图") {
      p <- p + geom_point(color = "#00D9FF", size = 3)
    } else {
      p <- p + geom_col(fill = "#00D9FF")
    }
    
    p + theme_minimal() +
      labs(title = "数据可视化", x = "X 轴", y = "Y 轴")
  })
  
  output$data_table <- renderTable({
    df %>% head(input$n_points) %>% summary()
  })
}

# 运行应用
shinyApp(ui = ui, server = server)
