import gymnasium as gym

env=gym.make("CartPole-v1",render_mode="human")

observation,info=env.reset(seed=42)
steps=0
c=0
total=0

for _ in range(2500):
   env.render()
   if observation[2] > 0 : 
      if observation[3] > 0 :
         action = 1 
         observation, reward, terminated, truncated, info = env.step(action)
         steps += 1
         observation, reward, terminated, truncated, info = env.step(action)
         steps += 1
      else : 
         action = 0
         observation, reward, terminated, truncated, info = env.step(action)
         steps += 1
   else : 
      if observation[3] < 0 :
         action = 0 
         observation, reward, terminated, truncated, info = env.step(action)
         steps += 1
         observation, reward, terminated, truncated, info = env.step(action)
         steps += 1
      else : 
         action = 1
         observation, reward, terminated, truncated, info = env.step(action)
         steps += 1

   if terminated or truncated:
      print(steps)
      c+=1
      total+=steps
      observation,info=env.reset()
      steps=0

env.close()
print(total//c)