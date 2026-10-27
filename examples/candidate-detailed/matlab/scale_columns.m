% Return A with each column scaled by its matching fixed weight.
function A = scale_columns(A)
% Build four column weights in one continued row-vector statement.
weights = [1, 2, ...
           3, 4];
% Compute row means across columns; this local result is not used below.
means = mean(A, 2);
% Select the first row and all columns; this local result is unused below.
first = A(1, :);
% Conjugate-transpose A; the resulting local B is not used below.
B = A';
% Visit each column using MATLAB one-based indices.
for k = 1:size(A, 2)
    % Scale all rows in column k by weight k; more than four columns
    % accesses beyond the four weights and raises an indexing error.
    A(:, k) = A(:, k) * weights(k);
end
end
