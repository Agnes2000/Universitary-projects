size(out.pout)

p_array = squeeze(out.pout)';

size(out.pdout)

pd_array = squeeze(out.pdout)';

plot3(pd_array(:,1), pd_array(:,2), pd_array(:,3), 'r', 'LineWidth', 2); hold on;
plot3(p_array(:,1),  p_array(:,2),  p_array(:,3),  'b--', 'LineWidth', 1.5);
grid on; axis equal; view(3);
xlabel('x'); ylabel('y'); zlabel('z');
legend('Desired', 'Actual');
