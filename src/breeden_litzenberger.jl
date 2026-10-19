"""
Calcul Julia de la densité de Breeden–Litzenberger à partir d'une courbe
de calls lissée. Aucun package externe n'est requis.

Entrée : results/reconstructed_call_grid.csv
Sortie : results/rnd_julia.csv et results/julia_diagnostics.txt
"""

using DelimitedFiles
using Printf

root = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(root, "results", "reconstructed_call_grid.csv")
output_path = joinpath(root, "results", "rnd_julia.csv")
diag_path = joinpath(root, "results", "julia_diagnostics.txt")

raw, header = readdlm(input_path, ',', header=true)
names = vec(header)
strike_col = findfirst(==("strike"), names)
call_col = findfirst(==("call_price"), names)
strike_col === nothing && error("Colonne strike absente")
call_col === nothing && error("Colonne call_price absente")

K = Float64.(raw[:, strike_col])
C = Float64.(raw[:, call_col])
n = length(K)
n >= 5 || error("Grille trop courte")

function first_derivative(x::Vector{Float64}, y::Vector{Float64})
    n = length(x)
    d = zeros(n)
    d[1] = (y[2] - y[1]) / (x[2] - x[1])
    d[end] = (y[end] - y[end-1]) / (x[end] - x[end-1])
    for i in 2:n-1
        d[i] = (y[i+1] - y[i-1]) / (x[i+1] - x[i-1])
    end
    d
end

function trapz(x::Vector{Float64}, y::Vector{Float64})
    sum((x[2:end] .- x[1:end-1]) .* (y[2:end] .+ y[1:end-1]) ./ 2)
end

# Le discount factor est lu dans diagnostics.json sans parseur JSON externe.
diag_json = read(joinpath(root, "results", "diagnostics.json"), String)
matched = match(r"\"discount_factor_from_parity\":\s*([0-9.eE+-]+)", diag_json)
matched === nothing && error("Discount factor introuvable")
discount = parse(Float64, matched.captures[1])

dC = first_derivative(K, C)
d2C = first_derivative(K, dC)
q_raw = d2C ./ discount
q_positive = max.(q_raw, 0.0)
mass_raw = trapz(K, q_raw)
mass_positive = trapz(K, q_positive)
q = q_positive ./ mass_positive
mean_q = trapz(K, K .* q)
variance_q = trapz(K, (K .- mean_q).^2 .* q)
negative_fraction = sum(q_raw .< -1e-10) / n
material_negative_fraction = sum(q_raw .< -1e-3 * maximum(q_raw)) / n
negative_mass = trapz(K, max.(-q_raw, 0.0))

open(output_path, "w") do io
    println(io, "strike,call_price,rnd_raw,rnd_normalized")
    for i in eachindex(K)
        @printf(io, "%.10f,%.10f,%.14g,%.14g\n", K[i], C[i], q_raw[i], q[i])
    end
end

open(diag_path, "w") do io
    @printf(io, "discount_factor=%.12f\n", discount)
    @printf(io, "raw_density_mass_on_grid=%.12f\n", mass_raw)
    @printf(io, "positive_mass_before_normalization=%.12f\n", mass_positive)
    @printf(io, "negative_grid_fraction=%.12f\n", negative_fraction)
    @printf(io, "material_negative_grid_fraction_below_0.1pct_peak=%.12f\n", material_negative_fraction)
    @printf(io, "absolute_negative_mass=%.12f\n", negative_mass)
    @printf(io, "normalized_density_mean=%.12f\n", mean_q)
    @printf(io, "normalized_density_std=%.12f\n", sqrt(variance_q))
end

@printf("Julia BL completed: %d grid points, mass %.6f, mean %.3f\n", n, mass_raw, mean_q)
