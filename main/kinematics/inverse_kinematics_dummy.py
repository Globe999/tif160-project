import numpy as np

def dumb_but_optimized_inverse_kinematics(x, y, z):
    # Define angle ranges
    theta0_range = np.arange(-90, 91, 1) * np.pi / 180  # range for theta0 (0 to 180 degrees)
    theta1_range = np.arange(0, 181, 1) * np.pi / 180  # range for theta1 (0 to 180 degrees)
    theta2_range = np.arange(-90, 91, 1) * np.pi / 180   # range for theta2 (0 to 90 degrees)

    # length parameters of robot
    L2 = 0.32
    L3 = 0.045
    L4 = 0.108
    L5 = 0.005
    L6 = 0.034
    L7 = 0.015
    L8 = 0.088
    L9 = 0.204

    # Target point
    true = np.array([x, y, z])

    # Meshgrid for theta0, theta1, theta2
    theta0_grid, theta1_grid, theta2_grid = np.meshgrid(theta0_range, theta1_range, theta2_range,indexing='ij')

    # Compute x2, y2, z2 for all theta2 (translation from frame 3 to frame 2)
    x2 = - np.sin(theta2_grid) * (-L9)  
    y2 =  + np.cos(theta2_grid) * (-L9)
    z2 = 0

    # Compute x1, y1, z1 for all theta1 (translation from frame 2 to frame 1)
    x1 = np.cos(theta1_grid) * (x2 + L7) - np.sin(theta1_grid) * (y2 - L8)
    y1 = np.sin(theta1_grid) * (x2 + L7) + np.cos(theta1_grid) * (y2 - L8)
    z1 = z2 - L5

    # Compute x0, y0, z0 for all theta0 (translation from frame 1 to frame 0)
    x0 = np.cos(theta0_grid) * (x1 + L6) - np.sin(theta0_grid) * (-z1 - L4)
    y0 = np.sin(theta0_grid) * (x1 + L6) + np.cos(theta0_grid) * (-z1 - L4)
    z0 = y1 + (L2 + L3)
    
    print(np.size(x0),np.size(y0),np.size(z0))
    # Calculate Euclidean distance between all generated points and the target point
    dist = np.sqrt((x0 - x)**2 + (y0 - y)**2 + (z0 - z)**2)
    print(np.size(dist))
    # Find the index of the smallest distance
    min_index = np.unravel_index(np.argmin(dist), dist.shape)
    print(np.argmin(dist))
    print(x0[min_index],y0[min_index],z0[min_index])
    # Extract the best angles corresponding to the minimum distance
    best_theta0 = theta0_range[min_index[0]]
    best_theta1 = theta1_range[min_index[1]]
    best_theta2 = theta2_range[min_index[2]]
    
    print("Best Distance:", dist[min_index])
    return best_theta0*180/np.pi, best_theta1*180/np.pi, best_theta2*180/np.pi



# function to calculate point p
# def calc_kinematics(theta0,theta1,theta2,x3 = 0,y3 = 0, z3 = 0):
#     L2 = 0.32
#     L3 = 0.045
#     L4 = 0.108
#     L5 = 0.005
#     L6 = 0.034
#     L7 = 0.015
#     L8 = 0.088
#     L9 = 0.204
#     #translation from frame 3 to frame 2
#     x2 = np.cos(theta2)*x3 - np.sin(theta2)*(y3 - L9)
#     y2 = np.sin(theta2)*x3 + np.cos(theta2)*(y3 - L9)
#     z2 = z3

#     #translation frame 2 to frame 1
#     x1 = np.cos(theta1)*(x2 + L7) - np.sin(theta1)*(y2 - L8)
#     y1 = np.sin(theta1)*(x2 + L7) + np.cos(theta1)*(y2 - L8)
#     z1 = z2 - L5

#     #translation frame 1 to frame 0
#     x0 = np.cos(theta0)*(x1 + L6) - np.sin(theta0)*(-z1 - L4)
#     y0 = np.sin(theta0)*(x1 + L6) + np.cos(theta0)*(-z1 - L4)
#     z0 = y1 +(L2+L3)

#     #print results
#     print("The Coordinates of point P: ")
#     print('x0 = %.3f' % x0)
#     print('y0 = %.3f' % y0)
#     print('z0 = %.3f' % z0)

#     #return point
#     return x0,y0,z0

#calculate for given angles
# Test the optimized inverse kinematics function

# i,j,k = dumb_but_optimized_inverse_kinematics(0.11,-0.11,0.2)
# x0,y0,z0 = calc_kinematics(i*np.pi/180,j*np.pi/180,k*np.pi/180)
# dist = np.sqrt((x0-0.11)**2 + (y0+0.11)**2 + (z0 - 0.2)**2)
# print(dist)
# print(i,j,k)


# import numpy as np

# # Simplified Inverse Kinematics Function for Debugging
# def debug_inverse_kinematics(x, y, z):
#     # Define a smaller angle range for debugging
#     theta0_range = np.arange(-90, 91, 2) * np.pi / 180  # steps of 15 degrees
#     theta1_range = np.arange(0, 121, 2) * np.pi / 180   # steps of 15 degrees
#     theta2_range = np.arange(-90, 91, 2) * np.pi / 180  # steps of 15 degrees

#     # Length parameters (as given)
#     L2 = 0.32
#     L3 = 0.045
#     L4 = 0.108
#     L5 = 0.005
#     L6 = 0.034
#     L7 = 0.015
#     L8 = 0.088
#     L9 = 0.204

#     # Target point
#     target_point = np.array([x, y, z])
    
#     best_distance = float('inf')
#     best_theta0, best_theta1, best_theta2 = None, None, None

#     # Loop through all combinations of theta0, theta1, theta2
#     for theta0 in theta0_range:
#         for theta1 in theta1_range:
#             for theta2 in theta2_range:
#                 # Calculate the position of the end effector using forward kinematics
#                 x0, y0, z0 = calc_kinematics(theta0, theta1, theta2)

#                 # Calculate the Euclidean distance to the target point
#                 distance = np.sqrt((x0 - x)**2 + (y0 - y)**2 + (z0 - z)**2)

#                 # Debug print to track positions and distances
#                 #print(f"Theta0: {theta0*180/np.pi:.2f}, Theta1: {theta1*180/np.pi:.2f}, Theta2: {theta2*180/np.pi:.2f} -> x0: {x0:.4f}, y0: {y0:.4f}, z0: {z0:.4f}, Distance: {distance:.4f}")

#                 # Update best angles if a closer point is found
#                 if distance < best_distance:
#                     best_distance = distance
#                     best_theta0, best_theta1, best_theta2 = theta0, theta1, theta2

#     print(f"\nBest Distance: {best_distance}")
#     return best_theta0*180/np.pi, best_theta1*180/np.pi, best_theta2*180/np.pi

# # Simplified Forward Kinematics
# def calc_kinematics(theta0, theta1, theta2, x3=0, y3=0, z3=0):
#     # Robot link lengths
#     L2 = 0.32
#     L3 = 0.045
#     L4 = 0.108
#     L5 = 0.005
#     L6 = 0.034
#     L7 = 0.015
#     L8 = 0.088
#     L9 = 0.204
    
#     # Transformation from frame 3 to frame 2
#     x2 = np.cos(theta2) * x3 - np.sin(theta2) * (y3 - L9)
#     y2 = np.sin(theta2) * x3 + np.cos(theta2) * (y3 - L9)
#     z2 = z3

#     # Transformation from frame 2 to frame 1
#     x1 = np.cos(theta1) * (x2 + L7) - np.sin(theta1) * (y2 - L8)
#     y1 = np.sin(theta1) * (x2 + L7) + np.cos(theta1) * (y2 - L8)
#     z1 = z2 - L5

#     # Transformation from frame 1 to frame 0
#     x0 = np.cos(theta0) * (x1 + L6) - np.sin(theta0) * (-z1 - L4)
#     y0 = np.sin(theta0) * (x1 + L6) + np.cos(theta0) * (-z1 - L4)
#     z0 = y1 + (L2 + L3)

#     return x0, y0, z0

# # Test the simplified inverse kinematics function
# best_theta0, best_theta1, best_theta2 = debug_inverse_kinematics(0.11, -0.11, 0.2)
# x0, y0, z0 = calc_kinematics(best_theta0*np.pi/180, best_theta1*np.pi/180, best_theta2*np.pi/180)

# print(f"\nBest Angles: Theta0 = {best_theta0:.2f}, Theta1 = {best_theta1:.2f}, Theta2 = {best_theta2:.2f}")
# print(f"Forward Kinematics for Best Angles: x0 = {x0:.4f}, y0 = {y0:.4f}, z0 = {z0:.4f}")
