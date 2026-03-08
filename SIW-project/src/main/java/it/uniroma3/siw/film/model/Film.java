package it.uniroma3.siw.film.model;

import static javax.persistence.CascadeType.ALL;
import static javax.persistence.GenerationType.AUTO;

import java.util.LinkedList;
import java.util.List;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.JoinTable;
import javax.persistence.ManyToMany;
import javax.persistence.ManyToOne;
import javax.persistence.OneToMany;
import javax.persistence.Transient;
import javax.validation.constraints.Max;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;

import lombok.Getter;
import lombok.Setter;
import lombok.Singular;

@Entity
@Getter @Setter
public class Film {
    
    @Id
    @GeneratedValue(strategy = AUTO)
    private Long id;

    @NotBlank
    @Size(min = 1, max = 40)
    private String nome;

    @NotNull
    @Max(2023)
    @Min(1895)
    private Short anno;

    @Singular
    @OneToMany(mappedBy = "film", cascade = ALL)
    private List<Recensione> recensioni;
    
    @ManyToMany
    @Singular
    @JoinTable(name = "Attori_dei_film", joinColumns = @JoinColumn(name = "film"), inverseJoinColumns = @JoinColumn(name = "attori"))
    private List<Attore> attori;
    
    @ManyToOne
    private Regista regista;
    
    private String urlImg;

    public Film(){
        this.attori = new LinkedList<>();
        this.recensioni = new LinkedList<>();
    }

    @Transient
    public String getPhotosImagePath() {
        if (this.urlImg == null || this.id == null)
            return null; 
        return "/film-img/" + this.urlImg;
    }
    
}
