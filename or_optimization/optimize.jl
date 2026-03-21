using JuMP, GLPK, CSV, DataFrames, Statistics

df = CSV.read("training_data.csv",DataFrame)
N= nrow(df)
avg_amt = mean(df.amount)
std_amt =std(df.amount)
M = 100000 #must be larger than any possible transaction amount

model = Model(GLPK.Optimizer)

@variable(model, 1.0 <= threshold <= 5.0) 
@variable(model, flagged[1:N], Bin)

#Big M constraint
#force flagged[i] to be 1 if the amount is high enough
for i in 1:N
    @constraint(model, df.amount[i] >= (avg_amt + threshold * std_amt) - M * (1 - flagged[i]))
end

@objective(model, Max, sum(df.is_fraud[i] * flagged[i] for i in 1:N))

#only allow 1% false positive rate
@constraint(model, sum((1 - df.is_fraud[i]) * flagged[i] for i in 1:N) <= 0.01 * N)

optimize!(model)
println("Optimal Threshold: ",value(threshold))