# FitLayout - Python GNN Demo
# (c) 2023 Josef Katrnak
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# A basic GNN training loop implementation.

import torch.nn

class Train:
    def __init__(self, model, dataloader, val_dataloader, params):
        """
        Inits training procedure

        :param model: Input nn model
        :param dataloader: Dataloader with data
        :param val_dataloader: Dataloader with validation data
        :param params: Training parameters (epochs, learning_rate, weight_decay, eps)
        """
        self.model = model
        self.dataloader = dataloader
        self.val_dataloader = val_dataloader
        self.epochs = params["epochs"]

        # Use cross entropy as loss function
        self.criterion = torch.nn.CrossEntropyLoss()
        # Use AdamW as optimizer
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=params["learning_rate"],
                                           weight_decay=params["weight_decay"], eps=params["eps"])
        # Use Cosine Annealing LR as scheduler
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, len(self.dataloader))

    def train_batch(self):
        """
        Performs one step of training.

        :return: loss
        """
        total_loss = 0

        for i, data in enumerate(self.dataloader):
            # Clear gradients
            self.optimizer.zero_grad()
            # Forward pass
            outs = self.model(data.x, data.edge_index)
            # Compute the loss based on the training nodes (boxes)
            loss = self.criterion(outs[data.train_mask], data.y[data.train_mask])
            # Derive gradients
            loss.backward()

            # Update parameters
            self.optimizer.step()

            total_loss += loss
            #print(f'Batch {i + 1}, loss = {loss}')

        # decrease learning rate
        self.scheduler.step()

        return total_loss / len(self.dataloader)

    def validate(self):
        """
        Performs validation on a separate validation dataset.

        :return: validation loss
        """
        self.model.eval()  # Set the model to evaluation mode
        total_loss = 0
        
        with torch.no_grad():  # Disable gradient computation
            for data in self.val_dataloader:
                # Forward pass
                outs = self.model(data.x, data.edge_index)
                # Compute the loss based on the validation nodes (boxes)
                loss = self.criterion(outs[data.train_mask], data.y[data.train_mask])
                total_loss += loss.item()

        self.model.train()  # Set the model back to training mode
        return total_loss / len(self.val_dataloader)

    def train_loop(self):
        """
        Performs training loop.
        """
        print("Starting training loop ...\n")
        self.model.train()
        best_loss = float('inf')
        patience = 10
        no_improve = 0

        for e in range(1, self.epochs + 1):
            print(f'--- Epoch {e}')
            print('======================')
            epoch_loss = self.train_batch()
            val_loss = self.validate()
            print(f'Train loss: {epoch_loss:.4f}, Validation loss: {val_loss:.4f}')

            if val_loss < best_loss:
                best_loss = val_loss
                no_improve = 0
                # You could save the model here
                # torch.save(self.model.state_dict(), 'best_model.pth')
            else:
                no_improve += 1

            if no_improve >= patience:
                print("Early stopping triggered")
                break

        print("Training completed.")
