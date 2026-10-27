function A = scale_columns(A)
weights = [1, 2, ...
           3, 4];
means = mean(A, 2);
first = A(1, :);
B = A';
for k = 1:size(A, 2)
    A(:, k) = A(:, k) * weights(k);
end
end
